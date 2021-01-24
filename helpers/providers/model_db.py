import aiohttp
from .provider import Provider
from icecream import ic
from bs4 import BeautifulSoup

BASE_URL = "http://modeldb.science/api/v1"
MAX_REQUEST_RETRY = 5

REGION_KEY = 'hippocampus'


class ModelDbProvider(Provider):
    def __init__(self):
        super(ModelDbProvider, self).__init__()
        self.id_prefix = 'model_db'
        self.source = 'ModelDB'

    async def search_models(self, start=0, hits_per_page=50):
        url = f"{BASE_URL}/models?modeling_application=NEURON"
        print(f"Fetch url {url}")
        try:
            items = []
            more_than_one_neuron_items = []
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    data = await response.json()
                    for model_id in data:
                        try:
                            model = await self.__get_single_item__(model_id)
                            if model is not None:
                                item = self.__map__item__(model)
                                is_from_hippocampus = len(list(filter(lambda a: REGION_KEY in a.lower(),
                                                                  item['source']['cell_types']))) > 0
                                if not is_from_hippocampus:
                                    continue
                            if 'cell_types' in item['source'] and item['source']['cell_types'] is not None and len(item['source']['cell_types']) > 1:
                                print(f"More than 1 neurons {item['source']['id']}")
                                more_than_one_neuron_items.append(item['source']['id'])
                            items.append(item)
                        except Exception as ex:
                            print(f"Exception with model {model_id} {ex}")
                    await session.close()
            return items
        except Exception as ex:
            print(ex)

    def map_models(self, items=[]):
        pass

    def __map__item__(self, item):
        assert (item is not None)
        storage_identifier = f"{self.id_prefix}-{item['id']}"
        cell_types = []
        channels = []
        model_types = []
        model_concepts = []
        modeling_applications = []
        papers = []
        description = ''
        try:
            if 'neurons' in item and 'value' in item['neurons'] and len(item['neurons']['value']) > 0:
                cell_types = list(map(lambda a: a['object_name'], item['neurons']['value']))
            if 'model_paper' in item and 'value' in item['model_paper'] and len(item['model_paper']['value']) > 0:
                papers = list(map(lambda a: a['object_name'], item['model_paper']['value']))
            if 'currents' in item and 'value' in item['currents'] and len(item['currents']['value']) > 0:
                channels = list(map(lambda a: a['object_name'], item['currents']['value']))
            if 'model_type' in item and 'value' in item['model_type'] and len(item['model_type']['value']) > 0:
                model_types = list(map(lambda a: a['object_name'], item['model_type']['value']))
            if 'model_concept' in item and 'value' in item['model_concept'] and len(item['model_concept']['value']) > 0:
                model_concepts = list(map(lambda a: a['object_name'], item['model_concept']['value']))
            if 'modeling_application' in item and 'value' in item['modeling_application'] and len(item['modeling_application']['value']) > 0:
                modeling_applications = list(map(lambda a: a['object_name'], item['modeling_application']['value']))
            if 'notes' in item:
                description = item['notes']['value']

            return {
                'identifier': storage_identifier,
                'source': {
                    'source_id': storage_identifier,
                    'id': item['id'],
                    'name': item['name'],
                    'class_id': item['class_id'],
                    'description': description,
                    'channels': channels,
                    'cell_types': cell_types,
                    'page_link': f"https://senselab.med.yale.edu/modeldb/ShowModel?model={item['id']}#tabs-1",
                    'download_link': item['download_link'],
                    'model_types': model_types,
                    'model_concepts': model_concepts,
                    'modeling_application': modeling_applications,
                    'papers': papers,
                    'source': self.source
                }
            }
        except Exception as ex:
            print(f'Exception on map item {ex}')
        return None

    @staticmethod
    async def __get_single_item__(id=None):
        assert (id is not None)
        url = f"{BASE_URL}/models/{id}"
        data = None
        print(f"Fetch url {url}")
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    data = await response.json()
                    additional_data = await ModelDbProvider.__get_download_link__(id)
                    return {**data, **additional_data}
            return None
        except Exception as ex:
            print(ex)

    @staticmethod
    async def __get_download_link__(id=None):
        assert (id is not None)
        url = f"https://senselab.med.yale.edu/modeldb/ShowModel?model={id}#tabs-1"
        download_link_anchor = await ModelDbProvider.__scrape_model_page__(url, 'downloadmodelzip')
        result = {}
        if download_link_anchor is not None:
            download_link = download_link_anchor['href']
            result['download_link'] = download_link if download_link.startswith('http') \
                else 'https://senselab.med.yale.edu' + download_link
        return result

    @staticmethod
    async def __get_readme(id=None):
        url = f"https://senselab.med.yale.edu/modeldb/ShowModel?model={id}#tabs-2"
        file_tree_table = await ModelDbProvider.__scrape_model_page__(url, 'filetreetable')
        result = {}
        if file_tree_table is not None:
            download_link = file_tree_table['href']
            result['download_link'] = download_link if download_link.startswith('http') \
                else 'https://senselab.med.yale.edu' + download_link
        return result



    @staticmethod
    async def __scrape_model_page__(url=None, resource_id=None):
        assert (url is not None)
        assert (resource_id is not None)
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    page = await response.read()
                    parsed_page = BeautifulSoup(page, features='html.parser')
                    element = parsed_page.find(id=resource_id)
                    await session.close()
                    return element
        except Exception as ex:
            print(f'Exception on scraping {ex}')
        await session.close()
        return None
