import os
import json
import aiohttp
from os.path import splitext
from icecream import ic
from bs4 import BeautifulSoup
from .provider import Provider

BASE_URL = "http://modeldb.science/api/v1"
MAX_REQUEST_RETRY = 5

config = {}
dir_path = os.getcwd()
try:
    with open(f'{dir_path}/config/model_db.json') as json_file:
        config = json.load(json_file)
except Exception as ex:
    ic(f'Exception on loading file {ex}')

region_key = config['region_key'] if 'region_key' in config else 'hippocampus'


class ModelDbProvider(Provider):
    def __init__(self):
        super(ModelDbProvider, self).__init__()
        self.id_prefix = 'model_db'
        self.source = 'ModelDB'

    async def search_models(self, start=0, hits_per_page=50):
        url = f"{BASE_URL}/models?modeling_application=NEURON"
        #ic(f"Fetch url {url}")
        try:
            items = []
            more_than_one_neuron_items = []
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    data = await response.json()
                    for model_id in data:
                        try:
                            model = await self.__get_single_item__(model_id)
                            if model is not None:
                                item = self.__map__item__(model)
                                is_from_hippocampus = len(list(filter(lambda a: region_key in a.lower(),
                                                                      item['source']['cell_types']))) > 0
                                if not is_from_hippocampus:
                                    continue
                            if 'cell_types' in item['source'] and item['source']['cell_types'] is not None and len(
                                    item['source']['cell_types']) > 1:
                                ic(f"More than 1 neurons {item['source']['id']}")
                                more_than_one_neuron_items.append(item['source']['id'])
                            items.append(item)
                        except Exception as ex:
                            ic(f"Exception with model {model_id} {ex}")
                    await session.close()
            return items
        except Exception as ex:
            ic(ex)
        return items

    def map_models(self, items=[]):
        pass

    def __map__item__(self, item):
        assert (item is not None)
        storage_identifier = f"{self.id_prefix}-{item['id']}"
        cell_types = []
        channels = []
        model_types = []
        model_concepts = []
        implementers = []
        modeling_applications = []
        papers = []
        receptors = []
        description = ''
        try:
            if 'neurons' in item and 'value' in item['neurons'] and len(item['neurons']['value']) > 0:
                cell_types = [a['object_name'] for a in item['neurons']['value']]
            if 'papers' in item and len(item['papers']) > 0:
                papers = item['papers']
            elif 'model_paper' in item and 'value' in item['model_paper'] and len(item['model_paper']['value']) > 0:
                papers = [{
                    'label': a['object_name']
                } for a in item['model_paper']['value']]
            if 'currents' in item and 'value' in item['currents'] and len(item['currents']['value']) > 0:
                channels = [a['object_name'] for a in item['currents']['value']]
            if 'model_type' in item and 'value' in item['model_type'] and len(item['model_type']['value']) > 0:
                model_types = [a['object_name'] for a in item['model_type']['value']]
            if 'model_concept' in item and 'value' in item['model_concept'] and len(item['model_concept']['value']) > 0:
                model_concepts = [a['object_name'] for a in item['model_concept']['value']]
            if 'modeling_application' in item and 'value' in item['modeling_application'] and len(
                    item['modeling_application']['value']) > 0:
                modeling_applications = [a['object_name'] for a in item['modeling_application']['value']]
            if 'implemented_by' in item and 'value' in item['implemented_by'] and len(item['implemented_by']['value']) > 0:
                implementers = [a['object_name'] for a in item['implemented_by']['value']]
            if 'notes' in item:
                description = item['notes']['value']
            if 'receptors' in item and 'value' in item['receptors'] and len(item['receptors']['value']) > 0:
                receptors = [a['object_name'] for a in item['receptors']['value']]
            return {
                'identifier': storage_identifier,
                'source': {
                    'source_id': storage_identifier,
                    'id': str(item['id']),
                    'name': item['name'],
                    'class_id': item['class_id'],
                    'description': description,
                    'channels': channels,
                    'cell_types': cell_types,
                    'page_link': f"https://senselab.med.yale.edu/modeldb/ShowModel?model={item['id']}#tabs-1",
                    'download_link': item['download_link'] if 'download_link' in item else None,
                    'model_types': model_types,
                    'model_concepts': model_concepts,
                    'implementers': implementers,
                    'modeling_application': modeling_applications,
                    'papers': papers,
                    'readme_link': item['readme_link'] if 'readme_link' in item else None,
                    'model_files': item['model_files'] if 'model_files' in item else None,
                    'receptors': receptors,
                    'type': 'single',
                    'source': self.source
                }
            }
        except Exception as ex:
            ic(f'Exception on map item {ex}')
        return None

    @staticmethod
    async def __get_single_item__(id=None):
        assert (id is not None)
        url = f"{BASE_URL}/models/{id}"
        data = None
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    data = await response.json()
                    additional_data = await ModelDbProvider.__get_additional_data__(id)
                    return {**data, **additional_data}
            return None
        except Exception as ex:
            ic(f"Exception on get model db single item {ex}")
        return None

    @staticmethod
    async def __get_additional_data__(id=None):
        assert (id is not None)
        result = {}
        try:
            download_link = await ModelDbProvider.__get_download_link__(id)
            readme_link = await ModelDbProvider.__get_readme__(id)
            model_files = await ModelDbProvider.__get_model_files__(id)
            papers_refs = await ModelDbProvider.__get_papers_refs__(id)
            if papers_refs:
                result['papers'] = papers_refs
            result['download_link'] = download_link
            result['readme_link'] = readme_link
            result['model_files'] = model_files
        except Exception as ex:
            ic(f"exception scrape page {ex}")
        return result

    @staticmethod
    async def __get_download_link__(id=None):
        assert (id is not None)
        url = f"https://senselab.med.yale.edu/modeldb/ShowModel?model={id}#tabs-1"
        results = await ModelDbProvider.__scrape_model_page__(url, '#downloadmodelzip')
        if results:
            download_link_anchor = results[0]
            if download_link_anchor is not None:
                download_link = download_link_anchor['href']
                return download_link if download_link.startswith('http') \
                    else 'https://senselab.med.yale.edu' + download_link
        return None

    @staticmethod
    async def __get_readme__(id=None):
        assert (id is not None)
        url = f"https://senselab.med.yale.edu/modeldb/ShowModel?model={id}#tabs-2"
        file_tree_table = None
        results = await ModelDbProvider.__scrape_model_page__(url, '#filetreetable')
        if results:
            file_tree_table = results[0]
        if file_tree_table is not None:
            link_children = file_tree_table.select(
                selector='tr > td#filetree > div#filetreediv > table > tbody > tr > td > a')
            for link in link_children:
                if link.contents is not None:
                    contents = list(map(lambda x: x.lower() if isinstance(x, str) else None, link.contents))
                    if 'readme' in contents:
                        readme_link = link.attrs['href']
                        if readme_link is not None:
                            return readme_link if readme_link.startswith('http') \
                                else 'https://senselab.med.yale.edu' + readme_link
        return None

    @staticmethod
    async def __get_model_files__(id=None):
        assert (id is not None)
        url = f"https://senselab.med.yale.edu/modeldb/ShowModel?model={id}#tabs-2"
        model_results = {}
        file_tree_table = None
        results = await ModelDbProvider.__scrape_model_page__(url, '#filetreetable')
        if results:
            file_tree_table = results[0]
        if file_tree_table is not None:
            link_children = file_tree_table.select(
                selector='tr > td#filetree > div#filetreediv > table > tbody > tr > td > a')
            for link in link_children:
                if link.contents is not None:
                    contents = list(map(lambda x: x.lower() if isinstance(x, str) else None, link.contents))
                    labels = list(filter(lambda x: isinstance(x, str), contents))
                    if labels is not None and len(labels) >= 1:
                        label = labels[0]
                        url = link.attrs['href'] if 'href' in link.attrs else None
                        if url is not None:
                            url_splitted = splitext(url)
                            is_mod_file = '.mod' in label or '.mod' in url_splitted[-1]
                            #ic(f'is mod file {label} - {url} - {is_mod_file} ')
                            if is_mod_file:
                                try:
                                    download_link_page = url if url.startswith(
                                        'http') else 'https://senselab.med.yale.edu' + url
                                    link_url = await ModelDbProvider.__get_model_download_link__(download_link_page)
                                    if link_url is not None:
                                        if link_url not in model_results:
                                            model_results[link_url] = label
                                except Exception as ex:
                                    ic(f"Exception on get model files {ex}")
                                    return list(map(lambda a: {
                                        'label': model_results[a],
                                        'url': a
                                    }, model_results))

        return list(map(lambda a: {
            'label': model_results[a],
            'url': a
        }, model_results))

    @staticmethod
    async def __get_papers_refs__(id=None):
        assert (id is not None)
        url = f"https://senselab.med.yale.edu/modeldb/ShowModel?model={id}#tabs-1"
        papers_ref = None
        try:
            results = await ModelDbProvider.__scrape_model_page__(url, '#reference')
            if results:
                reference = results[0]
                links = reference.select('small > a')
                if links is not None and len(links) > 0:
                    paper_link = links[0]
                    if paper_link:
                        papers_ref = [{
                            'label': reference.contents[0].strip(),
                            'url': paper_link.attrs[
                                'href'] if paper_link.attrs is not None and 'href' in paper_link.attrs else None
                        }]
        except Exception as ex:
            ic(f'Exception on get papers {ex}')
        return papers_ref

    @staticmethod
    async def __get_model_download_link__(url):
        assert (url is not None)
        elements = await ModelDbProvider.__scrape_model_page__(url, '#downloadzip2')
        if elements:
            download_button = elements[0]
            if download_button is not None:
                return download_button.attrs['href'] if download_button.attrs['href'].startswith('http') \
                    else 'https://senselab.med.yale.edu' + download_button.attrs['href']
        return None

    @staticmethod
    async def __scrape_model_page__(url=None, selector=None):
        assert (url is not None)
        assert (selector is not None)
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    page = await response.read()
                    parsed_page = BeautifulSoup(page, 'html5lib')
                    elements = parsed_page.select(selector)
                    await session.close()
                    return elements
        except Exception as ex:
            ic(f'Exception on scraping {ex}')
        await session.close()
        return None
