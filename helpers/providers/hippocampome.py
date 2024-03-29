import os
import aiohttp
import json
from time import sleep
from icecream import ic
from bs4 import BeautifulSoup, Tag
from functools import reduce
from constants import SLEEP_TIME
from helpers.download_helper import download_image
from helpers.create_connector import create_connector
from .provider import Provider

BASE_URL = 'http://hippocampome.org/php/search_engine_json.php?query_str='

config = {}
dir_path = os.getcwd()
try:
    with open(f'{dir_path}/config/hippocampome.json') as json_file:
        config = json.load(json_file)
except Exception as ex:
    ic(f'Exception on loading file {ex}')

search_layers = config['layers'] if 'layers' in config else {}
search_markers = config['markers'] if 'markers' in config else []
search_morphologies = config['morphologies'] if 'morphologies' in config else []


class HippocampomeProvider(Provider):

    def __init__(self):
        super(HippocampomeProvider, self).__init__()
        self.id_prefix = 'hippocampome'
        self.source = 'Hippocampome'

    async def search_datasets(self, start=0, hits_per_page=50):
        items = []
        try:
            #neurons = []
            neurons = await self.__search_neurons__(start, hits_per_page)
            connections = await self.__search_connections__(start, hits_per_page)
            items.extend(neurons)
            items.extend(connections)
        except Exception as ex:
            ic(f'Exception on hippocampome')
        return items

    async def __search_neurons__(self, start=0, hits_per_page=50):
        neurons = []
        markers_str = ' OR '.join([f'D±:{marker} OR I±:{marker}' for marker in search_markers])
        try:
            layers_repr = [f"{search_layers[x]['key']}:{search_layers[x]['layers']}" for x in search_layers.keys()]
            morphologies_str = ' OR '.join(
                [f"{morphology}:{layer}" for morphology in search_morphologies for layer in layers_repr])
            url = BASE_URL + f'Neuron:(Presynaptic:(Markers:({markers_str}) OR Morphology:({morphologies_str})) AND Postsynaptic:(Markers:({markers_str}) OR Morphology:({morphologies_str})))'
            ic(f'Fetch hippocampome for neurons at {url}')
            async with aiohttp.ClientSession(connector=create_connector()) as session:
                response = await session.get(url)
                ic(f'Response status {response.status}')
                if response is not None and response.status == 200:
                    result = await response.json()
                    ic(f'Result length {len(result)}')
                    for index in result:
                        try:
                            neuron_data = await self.__scrape_data_page__(result[index]['source_id'],
                                                                          type='electrophysiology')
                            neurons.append(neuron_data)
                        except Exception as ex:
                            ic(f'Exception on neuron {index} {ex}')
                    ic(f'Neurons length {len(neurons)}')
                await session.close()
        except Exception as ex:
            ic(f'Exception on creating query {ex}')
        sleep(SLEEP_TIME)
        return neurons

    async def __search_connections__(self, start=0, hits_per_page=50):
        connections = []
        markers_str = ' OR '.join([f'D±:{marker} OR I±:{marker}' for marker in search_markers])
        try:
            layers_repr = [f"{search_layers[x]['key']}:{search_layers[x]['layers']}" for x in search_layers.keys()]
            morphologies_str = ' OR '.join(
                [f"{morphology}:{layer}" for morphology in search_morphologies for layer in layers_repr])
            url = BASE_URL + f'Connection:(Presynaptic:(Markers:({markers_str}) OR Morphology:({morphologies_str})) AND Postsynaptic:(Markers:({markers_str}) OR Morphology:({morphologies_str})))'
            ic(f'Fetch hippocampome for connections at {url}')
            async with aiohttp.ClientSession(connector=create_connector()) as session:
                response = await session.get(url)
                ic(f'Response status {response.status}')
                if response is not None and response.status == 200:
                    result = await response.json()
                    ic(f'Result length {len(result)}')
                    for index in result:
                        ic(f'Processing connection {index}')
                        try:
                            source_id = result[index]['source_id']
                            destination_id = result[index]['destination_id']
                            presynaptic = await self.__scrape_data_page__(source_id)
                            postsynaptic = await self.__scrape_data_page__(destination_id)
                            connections.append({
                                'identifier': f'{self.id_prefix}-{source_id}-{destination_id}',
                                'source': {
                                    'presynaptic': presynaptic['source'],
                                    'postsynaptic': postsynaptic['source'],
                                    'type': 'connection',
                                    'source': self.source
                                }
                            })
                        except Exception as ex:
                            ic(f'Exception on connection {index} {ex}')
                    ic(f'Connections length {len(connections)}')
                await session.close()
        except Exception as ex:
            ic(f'Exception on creating query {ex}')

        sleep(SLEEP_TIME)
        return connections

    async def __scrape_data_page__(self, id, type=None):
        assert (id is not None)
        data = {}
        url = f'http://hippocampome.org/php/neuron_page.php?id={id}'
        try:
            async with aiohttp.ClientSession(connector=create_connector()) as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    page = await response.read()
                    if page:
                        parsed_page = BeautifulSoup(page, 'html5lib')
                        tables = parsed_page.select('table.body_table > tbody > tr > td > table')
                        if tables:
                            name = self.__extract_name__(tables)
                            icon = await self.__extract_representantive_figure__(tables)
                            papers = self.__extract_papers__(tables)
                            markers = self.__extract_markers__(tables)
                            regions, layers = self.__extract_regions_and_layers__(tables)
                            data['name'] = name
                            data['icon'] = icon
                            data['papers'] = papers
                            data['markers'] = list(set(filter(lambda a: a is not None and a != '', markers)))
                            data['secondary_region'] = list(set(regions))
                            data['layers'] = list(set(layers))
        except Exception as ex:
            ic(f'Exception on do data scrape {ex}')

        storage_identifier = f"{self.id_prefix}-{id}"
        data['id'] = f'{id}'
        data['source_id'] = storage_identifier
        data['page_link'] = url
        data['source'] = self.source
        data['type'] = type

        neuron = {
            'identifier': f'{id}',
            'source': data
        }
        sleep(SLEEP_TIME)
        return neuron

    def map_models(self, items=[]):
        pass

    def __extract_name__(self, tables=[]):
        # FIND NAME
        try:
            table_rows = tables[1].select('tbody > tr')
            if table_rows:
                table_headers = table_rows[0].select('td')
                if table_headers:
                    name_header = table_headers[0]
                    labels = name_header.contents
                    if labels:
                        name_header_label = labels[0].strip().lower()
                        if name_header_label == 'name':
                            table_values = table_rows[1].select('td')
                            if table_values:
                                values = table_values[1].contents
                                if values:
                                    name_value = values[0].strip()
                                    return name_value
        except Exception as ex:
            ic(f'Exception on extract name {ex}')
        return None

    def __extract_regions_and_layers__(self, tables=[]):
        regions = []
        layers = []
        try:
            if tables and len(tables) > 7:
                region_tags = tables[7].select('.table_neuron_page2 > a > font')
                if region_tags and len(region_tags) > 0:
                    regions.extend(x[0].strip(' \n\t') for x in [[content.split(':')[0] for content in region_tag.contents] for region_tag in region_tags])
                    extracted_layers = reduce(lambda a, b: a + b,
                                              [x for x in [[content.strip(' \n\t') for content in region_tag.contents] for region_tag in region_tags]])
                    layers.extend(extracted_layers)
            if tables and len(tables) > 8:
                region_tags = tables[8].select('.table_neuron_page2 > a > font')
                if region_tags and len(region_tags) > 0:
                    regions.extend(x[0].strip(' \n\t') for x in [[content.split(':')[0] for content in region_tag.contents] for region_tag in region_tags])
                    extracted_layers = reduce(lambda a, b: a + b,
                                              [x for x in [[content.strip(' \n\t') for content in region_tag.contents] for region_tag in region_tags]])
                    layers.extend(extracted_layers)
            if tables and len(tables) > 9:
                region_tags = tables[9].select('.table_neuron_page2 > a > font')
                if region_tags and len(region_tags) > 0:
                    regions.extend(x[0].strip(' \n\t') for x in [[content.split(':')[0] for content in region_tag.contents] for region_tag in region_tags])
                    extracted_layers = reduce(lambda a, b: a + b, [x for x in [[content.strip(' \n\t') for content in region_tag.contents] for region_tag in region_tags]])
                    layers.extend(extracted_layers)

        except Exception as ex:
            ic(f'Exception for regions {ex}')
        return list(set(regions)), list(set(layers))

    def __extract_papers__(self, tables=[]):
        papers = []
        try:
            representantive_figure_table_index = -1
            for index, table in enumerate(tables):
                table_elements = table.select('tbody > tr > td')
                if table_elements:
                    for elem in table_elements:
                        contents = elem.contents
                        if contents:
                            for content in contents:
                                if isinstance(content, str) and content.strip(' \n\t').lower() == 'representative figure':
                                    representantive_figure_table_index = index
                                    break
            if representantive_figure_table_index > -1 and len(tables) > representantive_figure_table_index + 1:
                table = tables[representantive_figure_table_index + 1]
                elements = table.select('tbody > tr > td.table_neuron_page2')
                if elements:
                    element = elements[0]
                    contents = element.contents
                    for index, content in enumerate(contents):
                        if isinstance(content, Tag) and content.name == 'strong' and \
                                reduce(lambda a, b: a or b, ['pmid' in item.lower() for item in content.contents], False):
                            pmid_link = contents[index + 1]
                            if isinstance(pmid_link, Tag) and pmid_link.name == 'a':
                                label = pmid_link.contents[1] if isinstance(pmid_link.contents[1], str) else \
                                    pmid_link.contents[1].contents[0]
                                papers.append({
                                    'label': label,
                                    'url': pmid_link.attrs['href']
                                })

        except Exception as ex:
            ic(f'Exctract paper exception {ex}')

        return papers

    async def __extract_representantive_figure__(self, tables=[]):
        try:
            representantive_figure_table_index = -1
            for index, table in enumerate(tables):
                table_elements = table.select('tbody > tr > td')
                if table_elements:
                    for elem in table_elements:
                        contents = elem.contents
                        if contents:
                            for content in contents:
                                if isinstance(content, str) and content.strip(' \n\t').lower() == 'representative figure':
                                    representantive_figure_table_index = index
                                    break
            if representantive_figure_table_index - 1 and len(tables) > representantive_figure_table_index + 2:
                table = tables[representantive_figure_table_index + 2]
                elements = table.select('tbody > tr > td')
                if elements:
                    for elem in elements:
                        images = elem.select('img')
                        if images:
                            image_url = images[0].attrs['src']
                            absolute_image_url = image_url if image_url.startswith(
                                'http') else f'http://hippocampome.org/php/{image_url}'
                            if absolute_image_url:
                                try:
                                    local_image_file_path = await download_image(absolute_image_url, self.source)
                                    image_file_path = f"{os.getenv('HOST')}{local_image_file_path}" if local_image_file_path is not None else None
                                    return image_file_path
                                except Exception as ex:
                                    ic(f'Exception download local image version {ex} - {absolute_image_url}')
        except Exception as ex:
            ic(f'Exception on extract representative figure {ex}')
        return None

    def __extract_markers__(self, tables=[]):
        markers = []
        try:
            representantive_figure_table_index = -1
            for index, table in enumerate(tables):
                table_elements = table.select('tbody > tr > td')
                if table_elements:
                    for elem in table_elements:
                        contents = elem.contents
                        if contents:
                            for content in contents:
                                if isinstance(content, str) and content.strip(' \n\t').lower() == 'representative figure':
                                    representantive_figure_table_index = index
                                    break
            #positive markers
            if representantive_figure_table_index - 1 and len(tables) > representantive_figure_table_index + 4:
                table = tables[representantive_figure_table_index + 4]
                elements = table.select('tbody > tr > td.table_neuron_page2')
                if elements:
                    element = elements[0]
                    contents = element.contents
                    for content in contents:
                        if isinstance(content, Tag) and content.name == 'a':
                            if len(content.contents) > 0 and isinstance(content.contents[0], str):
                                label = content.contents[0].strip(' \n\t')
                                markers.append(label)
            #negative markers
            if representantive_figure_table_index - 1 and len(tables) > representantive_figure_table_index + 5:
                table = tables[representantive_figure_table_index + 5]
                elements = table.select('tbody > tr > td.table_neuron_page2')
                if elements:
                    element = elements[0]
                    contents = element.contents
                    for content in contents:
                        if isinstance(content, Tag) and content.name == 'a':
                            if len(content.contents) > 0 and isinstance(content.contents[0], str):
                                label = content.contents[0].strip(' \n\t')
                                markers.append(label)
            #mixed expression
            if representantive_figure_table_index - 1 and len(tables) > representantive_figure_table_index + 6:
                table = tables[representantive_figure_table_index + 6]
                elements = table.select('tbody > tr > td.table_neuron_page2')
                if elements:
                    element = elements[0]
                    contents = element.contents
                    for content in contents:
                        if isinstance(content, Tag) and content.name == 'a':
                            if len(content.contents) > 0 and isinstance(content.contents[0], str):
                                label = content.contents[0].strip(' \n\t')
                                markers.append(label)
            return list(set(markers))
        except Exception as ex:
            ic(f'Exception on extract representative figure {ex}')
        return None

