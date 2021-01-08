import requests
from .provider import Provider

BASE_URL = "http://neuromorpho.org/api"

class NeuroMorphoProvider(Provider):

    def __init__(self):
        super(NeuroMorphoProvider, self).__init__()
        self.session = requests.session()

    def search(self):
        url = lambda page, size: f"{BASE_URL}/neuron/select?page={page}&ssize={size}"
        num_page = 0
        size = 50
        params = {
            'brain_region': ['hippocampus']
        }
        try:
            fetched = False
            total_pages = 1
            all_items = []
            while num_page < (total_pages - 1) or fetched is False:
                response = self.session.post(url(num_page, size), json=params)
                if response is not None and response.status_code == 200:
                    data = response.json()
                    all_items.extend(self.map_datasets(data['_embedded']['neuronResources']))
                    total_pages = data['page']['totalPages']
                    num_page = num_page + 1
                    fetched = True
            return all_items
        except Exception as ex:
            raise ex

    def map_datasets(self, datasets=[]):
        try:
            mapped_datasets = [self.__map_dataset__(x) for x in datasets]
            return mapped_datasets
        except Exception as ex:
            print(ex)
            raise ex

    def __map_dataset__(self, dataset):
        return {
            'id': dataset['neuron_id'],
            'name': dataset['neuron_name'],
            'description': dataset['note'],
            'region': dataset['brain_region'],
            'cell_type': dataset['cell_type'].reversed(),
            'species': dataset['species'],
            'icon': dataset['png_url'],
            'link': dataset['self']['href'],
            'original_format': dataset['original_format'],
            'methods': dataset['protocol'],
            'morphologies': dataset['attributes'],
            'structural_domains': dataset['domain']
        }
