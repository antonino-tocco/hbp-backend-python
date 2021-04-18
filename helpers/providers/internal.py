import os
import json
from .provider import Provider


class InternalProvider(Provider):

    def __init__(self):
        super(InternalProvider, self).__init__()
        self.id_prefix = 'internal'
        self.source = 'internal'

    async def search_datasets(self, start=0, hits_per_page=50):
        dir_path = os.getcwd()
        mapped_items = []
        try:
            with open(f'{dir_path}/data/internal.json') as json_file:
                items = json.load(json_file)
                mapped_items = [self.__map__item__(item) for item in items]
            return mapped_items
        except Exception as ex:
            print(ex)
        return mapped_items

    def __map__item__(self, dataset):
        storage_identifier = f"{self.id_prefix}-{dataset['neuron_id']}"
        try:
            return {
                'identifier': storage_identifier,
                'source': {
                    'source_id': storage_identifier,
                    'id': str(dataset['neuron_id']),
                    'type': 'morphology',
                    'name': dataset['neuron_name'],
                    'download_link': dataset['download_link'],
                    'source': self.source
                }
            }
        except Exception as ex:
            return None