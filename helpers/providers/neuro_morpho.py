import math
import aiohttp
import os
import json
from bs4 import BeautifulSoup
from icecream import ic
from time import sleep
from functools import reduce
from constants import SLEEP_TIME
from helpers.download_helper import download_image
from .provider import Provider

BASE_URL = "http://neuromorpho.org/api"
MAX_REQUEST_RETRY = 5

config = {}
dir_path = os.getcwd()
try:
    with open(f'{dir_path}/config/neuro_morpho.json') as json_file:
        config = json.load(json_file)
except Exception as ex:
    ic(f'Exception on loading file {ex}')

domains = config['domains'] if 'domains' in config else {}
attributes = config['attributes'] if 'attributes' in config else []
physical_integrities = config['physical_integrities'] if 'physical_integrities' in config else []


def filter_values(values, allowed_values=[], not_allowed_values=[], exact=True):
    if values:
        return list(filter(lambda value: (
                reduce(lambda a, b: (a and b),
                       [allowed in list(map(lambda x: x.strip(' \n\t').lower(), value.split(','))) for allowed in
                        allowed_values] if exact else [allowed in value for allowed in allowed_values], True) and
                reduce(lambda a, b: (a and b),
                       [not_allowed not in list(map(lambda x: x.strip(' \n\t').lower(), value.split(','))) for not_allowed in
                        not_allowed_values] if exact else [not_allowed not in value for not_allowed in not_allowed_values],
                       True)
        ), values))
    return []


class NeuroMorphoProvider(Provider):
    def __init__(self):
        super(NeuroMorphoProvider, self).__init__()
        self.source = 'Neuromorpho'
        self.id_prefix = 'neuromorpho'

    async def get_all_field_value(self, field_name, num_retry=0):
        num_page = 0
        size = 100
        fetched = False
        total_pages = 1
        all_values = []
        while num_page <= (total_pages - 1) or fetched is False:
            url = f"{BASE_URL}/neuron/fields/{field_name}?page={num_page}&size={size}"
            ic(f'Fetch url {url} Retry {num_retry}')
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                    async with session.get(url, allow_redirects=True, timeout=30) as response:
                        #ic(f'Response status for url {url} {response.status}')
                        if response is not None and response.status == 200:
                            data = await response.json()
                            all_values.extend(data['fields'])
                            # ONLY FOR AVOID NEUROMORPHO ISSUE
                            sleep(SLEEP_TIME)
                        await session.close()
            except Exception as ex:
                ic(f"Exception retrieving field values {ex}")
                if num_retry < MAX_REQUEST_RETRY:
                    sleep(SLEEP_TIME)
                    return await self.get_all_field_value(field_name, num_retry=num_retry + 1)
            num_page = num_page + 1
            fetched = True
        return all_values

    async def search_datasets(self, start=0, hits_per_page=50):
        num_page = math.floor(start / hits_per_page)
        size = hits_per_page
        domain_allowed_values = filter_values(await self.get_all_field_value('domain'), domains['allowed'] if 'allowed' in domains else [], domains['not_allowed'] if 'not_allowed' in domains else [])
        #original_format_allowed_values = filter_values(await self.get_all_field_value('original_format'), ['.asc'],
        #                                               exact=False)
        attributes_allowed_values = filter_values(await self.get_all_field_value('attributes'),
                                                  attributes['allowed'] if 'allowed' in attributes else [], attributes['not_allowed'] if 'not_allowed' in attributes else [])
        physical_integrity_values = filter_values(await self.get_all_field_value('Physical_Integrity'),
                                                  physical_integrities['allowed'] if 'allowed' in physical_integrities else [], physical_integrities['not_allowed'] if 'not_allowed' in physical_integrities else [])
        ic(f"Domains {domain_allowed_values}")
        #ic(f"Original format {original_format_allowed_values}")
        ic(f"Attributes {attributes_allowed_values}")
        ic(f"Physical Integrity {physical_integrity_values}")
        params = {
            'brain_region': config['brain_regions'] if 'brain_regions' in config else ['hippocampus'],
            'domain': domain_allowed_values,
            #'original_format': original_format_allowed_values,
            'attributes': attributes_allowed_values,
            'Physical_Integrity': physical_integrity_values
        }
        try:
            fetched = False
            total_pages = 1
            all_items = []
            while num_page <= (total_pages - 1) or fetched is False:
                url = f"{BASE_URL}/neuron/select?page={num_page}&size={size}"
                items, total_pages = await self.__make_search_request__(url, params)
                all_items.extend(items)
                num_page = num_page + 1
                fetched = True
                #ONLY FOR AVOID NEUROMORPHO ISSUE
                sleep(SLEEP_TIME)
            return all_items
        except Exception as ex:
            ic(f'Exception on all_items ${ex}')
            raise ex

    async def map_datasets(self, items=[]):
        try:
            mapped_datasets = [await self.__map_dataset__(x) for x in items]
            mapped_datasets = list(filter(lambda a: a is not None, mapped_datasets))
            return mapped_datasets
        except Exception as ex:
            ic(f"Exception on map datasets {ex}")
            raise ex

    async def __make_search_request__(self, url, params, num_retry=0):
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                ic(f'Fetch url {url} Retry {num_retry}')
                async with session.post(url, json=params, allow_redirects=True, timeout=30) as response:
                    ic(f'Response status for url {url} {response.status}')
                    items = []
                    total_pages = 1
                    if response is not None and response.status == 200:
                        data = await response.json()
                        if data is not None and '_embedded' in data:
                            items = await self.map_datasets(data['_embedded']['neuronResources'])
                            items = await self.__filter_items__(items)
                            total_pages = data['page']['totalPages']
                    sleep(SLEEP_TIME)
                    await session.close()
                    return (items, total_pages)
        except Exception as ex:
            ic(f"exception retrieving values {ex}")
            if num_retry < MAX_REQUEST_RETRY:
                sleep(SLEEP_TIME)
                return await self.__make_search_request__(url, params=params, num_retry=num_retry + 1)
            else:
                return ([], 1)

    async def __map_dataset__(self, dataset):
        regions = dataset['brain_region']
        cell_types = dataset['cell_type']
        brain_region = ''
        secondary_region = ''
        primary_cell_type = ''
        secondary_cell_type = ''
        if len(regions) > 0:
            brain_region = regions[0]
        if len(regions) > 1:
            secondary_region = [regions[1]]

        if len(cell_types) > 0:
            primary_cell_type = cell_types[0]
        if len(cell_types) > 1:
            secondary_cell_type = cell_types[1]

        storage_identifier = f"{self.id_prefix}-{dataset['neuron_id']}"

        image_file_path = None
        if 'neuron_id' in dataset:
            original_format_url = await self.__retrieve_original_format_file__(str(dataset['neuron_id']))
            if original_format_url is not None and \
                    (os.path.splitext(original_format_url)[-1].lower() == '.asc'\
                    or os.path.splitext(original_format_url)[-1].lower() == '.swc'):

                try:
                    if dataset['png_url']:
                        local_image_file_path = await download_image(dataset['png_url'], self.source)
                        image_file_path = f"{os.getenv('HOST')}{local_image_file_path}" if local_image_file_path is not None else None
                except Exception as ex:
                    ic(f'Exception download image {ex}')

                #f"http://neuromorpho.org/dableFiles/{dataset['archive'].lower()}/Source-Version/{dataset['neuron_name']}.{original_format_ext}",

                try:
                    return {
                    'identifier': storage_identifier,
                    'source': {
                        'source_id': storage_identifier,
                        'id': str(dataset['neuron_id']),
                        'type': 'morphology',
                        'name': dataset['neuron_name'],
                        'description': dataset['note'],
                        'archive': dataset['archive'],
                        'region': brain_region,
                        'secondary_region': secondary_region,
                        'cell_type': primary_cell_type,
                        'secondary_cell_type': secondary_cell_type,
                        'species': dataset['species'],
                        'icon': image_file_path,
                        'link': dataset['_links']['self']['href'],
                        'original_format': dataset['original_format'],
                        'physical_integrity': dataset['physical_Integrity'],
                        'download_link': original_format_url,
                        'page_link': f"http://neuromorpho.org/neuron_info.jsp?neuron_name={dataset['neuron_name']}",
                        'protocol': dataset['protocol'],
                        'morphologies': dataset['attributes'],
                        'structural_domains': dataset['domain'],
                        'source': self.source
                    }
                }
                except Exception as ex:
                    raise ex
        return None

    async def __filter_items__(self, items=[]):
        if items is None or len(items) == 0:
            return []
        filtered_items = []
        for item in items:
            try:
                if item['source']['download_link'] is not None and (
                        os.path.splitext(item['source']['download_link'].lower())[-1] == '.asc'
                        or os.path.splitext(item['source']['download_link'].lower())[-1] == '.swc'):
                    file_exists = await self.__check_if_file_exists__(item['source']['download_link'])
                    if file_exists:
                        filtered_items.append(item)
            except Exception as ex:
                ic(f"Exception {ex}")
                raise ex
        return filtered_items

    async def __retrieve_original_format_file__(self, neuron_id=None):
        assert(neuron_id is not None)
        try:
            url = f'http://neuromorpho.org/neuron_info.jsp?neuron_id={neuron_id}'
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    page = await response.read()
                    if page:
                        parsed_page = BeautifulSoup(page, 'html5lib')
                        links = parsed_page.select('.info > table a')
                        for link in links:
                            link_contents = [x.strip(' \t\n').lower() for x in link.contents]
                            for content in link_contents:
                                if content == 'morphology file (original)':
                                    if 'href' in link.attrs:
                                        original_format_file = link.attrs['href'] if link.attrs['href'].startswith(
                                            'http') else f"http://neuromorpho.org/{link.attrs['href']}"
                                        return original_format_file
                await session.close()
        except Exception as ex:
            ic(f'Exception retrieving original format file {ex}')
        return None

    async def __check_if_file_exists__(self, url=None) -> bool:
        assert (url is not None)
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                response = await session.get(url)
                file_existed = response.status == 200
                await session.close()
                return file_existed
        except Exception as ex:
            return False
