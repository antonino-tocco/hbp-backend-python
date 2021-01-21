import aiohttp
from .provider import Provider
from icecream import ic

BASE_URL = "http://modeldb.science/api/v1"
MAX_REQUEST_RETRY = 5

REGION_KEY = 'hippocampus'


class ModelDbProvider(Provider):
    def __init__(self):
        super(ModelDbProvider, self).__init__()
        self.id_prefix = 'model_db'
        self.source = 'Model DB'

    async def search(self, start=0, hits_per_page=50):
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
                                is_from_hippocampus = len(list(filter(lambda a: REGION_KEY in a['object_name'].lower(),
                                                                  item['source']['neurons']))) > 0
                                if not is_from_hippocampus:
                                    continue
                            if 'neurons' in item['source'] and item['source']['neurons'] is not None and len(item['source']['neurons']) > 1:
                                print(f"More than 1 neurons {item['source']['id']}")
                                more_than_one_neuron_items.append(item['source']['id'])
                            items.append(item)
                        except Exception as ex:
                            print(f"Exception with model {model_id} {ex}")
                    await session.close()
            return items
        except Exception as ex:
            print(ex)

    def map_items(self, items=[]):
        pass

    def __map__item__(self, item):
        assert (item is not None)
        storage_identifier = f"{self.id_prefix}-{item['id']}"
        neurons = []
        model_type = {}
        model_concept = {}
        modeling_application = {}
        papers = {}
        description = ''
        try:
            if 'neurons' in item and 'value' in item['neurons']:
                neurons = item['neurons']['value']
            if 'model_type' in item:
                model_type = item['model_type']
            if 'model_concept' in item:
                model_concept = item['model_concept']
            if 'modeling_application' in item:
                modeling_application = item['modeling_application']
            if 'papers' in item:
                papers = item['papers']
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
                    'neurons': neurons,
                    'model_type': list(map(lambda x: x['object_name'], model_type['value'])) if model_type is not None and 'value' in model_type else [],
                    'model_concept': list(map(lambda x: x['object_name'], model_concept['value'])) if model_concept is not None and 'value' in model_concept else [],
                    'modeling_application': list(map(lambda x: x['object_name'], modeling_application['value'])) if modeling_application is not None and 'value' in modeling_application else [],
                    'papers': list(map(lambda x: x['object_name'], papers['value'])) if papers is not None and 'value' in papers else [],
                    'source': self.source
                }
            }
        except Exception as ex:
            print(f'Exception on map item {ex}')
        return None

    async def __get_single_item__(self, id):
        url = f"{BASE_URL}/models/{id}"
        print(f"Fetch url {url}")
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    data = await response.json()
                    return data
            return None
        except Exception as ex:
            print(ex)