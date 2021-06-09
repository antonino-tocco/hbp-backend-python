import os
import json
from .provider import Provider


base_page_url = f'https://www.hippocampushub.eu/model/experimental-data/neuronal-electrophysiology'
base_image_url = f'https://www.hippocampushub.eu//model/assets/images/exp-morph-images/'


class InternalElectrophysiologyProvider(Provider):

    def __init__(self):
        super(InternalElectrophysiologyProvider, self).__init__()
        self.id_prefix = 'internal_electrophysiology'
        self.source = 'internal_electrophysiology'

    async def search_datasets(self, start=0, hits_per_page=50):
        dir_path = os.getcwd()
        mapped_items = []
        try:
            with open(f'{dir_path}/data/internal_electrophysiology.json') as json_file:
                items = json.load(json_file)
                mapped_items = [self.__map__item__(item) for item in items]
            return mapped_items
        except Exception as ex:
            print(ex)
        return mapped_items

    def __map__item__(self, dataset):
        storage_identifier = f"{self.id_prefix}-{dataset['neuron_id']}"
        cell_type = dataset['cell_type'] if 'cell_type' in dataset else None
        try:
            page_url = f"{base_page_url}?etype={cell_type}&etype_instance={dataset['neuron_id']}"
            image_url = f"{base_image_url}/{dataset['neuron_id']}.jpeg"
            return {
                'identifier': storage_identifier,
                'source': {
                    'source_id': storage_identifier,
                    'id': str(dataset['neuron_id']),
                    'type': 'electrophysiology',
                    'name': dataset['neuron_name'],
                    'page_link': page_url,
                    #'icon': image_url,
                    'source': self.source
                }
            }
        except Exception as ex:
            return None