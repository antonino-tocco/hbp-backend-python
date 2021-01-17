import aiohttp
from .provider import Provider

BASE_URL = "http://modeldb.science/api/v1"
MAX_REQUEST_RETRY = 5

class ModelDbProvider(Provider):
    def __init__(self):
        super(ModelDbProvider, self).__init__()
        self.id_prefix = 'model_db'
        self.source = 'Model DB'

    async def search(self, start=0, hits_per_page=50):
        url = f"{BASE_URL}/models"
        print(f"Fetch url {url}")
        try:
            items = []
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                if response is not None and response.status == 200:
                    data = await response.json()
                    for model_id in data:
                        model = await self.__get_single_item__(model_id)
                        items.append(self.__map__item__(model))
                    await session.close()
            return items
        except Exception as ex:
            print(ex)

    def map_items(self, items=[]):
        pass

    def __map__item__(self, item):
        assert (item is not None)
        storage_identfier = f"{self.id_prefix}-{item['id']}"
        neurons = []
        model_type = {}
        model_concept = {}
        modeling_application = {}
        papers = {}
        if 'neurons' in item:
            neurons = item['neurons']
        if 'model_type' in item:
            model_type = item['model_type']
        if 'model_concept' in item:
            model_concept = item['model_concept']
        if 'modeling_application' in item:
            modeling_application = item['modeling_application']
        if 'papers' in item:
            papers = item['papers']
        return {
            'identifier': storage_identfier,
            'source': {
                'source_id': storage_identfier,
                'id': item['id'],
                'name': item['name'],
                'class_id': item['class_id'],
                'description': item['notes']['value'],
                'neurons': item['neurons'],
                'model_type': list(map(lambda x: x['object_name'], model_type['value'])) if model_type is not None and 'value' in model_type else [],
                'model_concept': list(map(lambda x: x['object_name'], model_concept['value'])) if model_concept is not None and 'value' in model_concept else [],
                'modeling_application': list(map(lambda x: x['object_name'], modeling_application['value'])) if modeling_application is not None and 'value' in modeling_application else [],
                'papers': list(map(lambda x: x['object_name'], papers['value'])) if papers is not None and 'value' in papers else [],
                'source': self.source
            }
        }

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