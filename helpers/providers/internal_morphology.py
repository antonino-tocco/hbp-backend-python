import os
import json
from .provider import Provider


base_page_url = f'https://www.hippocampushub.eu/model/experimental-data/neuronal-morphology/'
base_image_url = f'https://www.hippocampushub.eu/model/assets/images/exp-morph-images/'


class InternalMorphologyProvider(Provider):

    def __init__(self):
        super(InternalMorphologyProvider, self).__init__()
        self.id_prefix = 'internal_morphology'
        self.source = 'internal_morphology'

    async def search_datasets(self, start=0, hits_per_page=50):
        dir_path = os.getcwd()
        mapped_items = []
        try:
            with open(f'{dir_path}/data/internal_morphology.json') as json_file:
                items = json.load(json_file)
                mapped_items = [self.__map__item__(item) for item in items]
            return mapped_items
        except Exception as ex:
            ic(ex)
        return mapped_items

    def __map__item__(self, dataset):
        storage_identifier = f"{self.id_prefix}-{dataset['neuron_id']}"
        region = dataset['region'] if 'region' in dataset else 'hippocampus'
        species = dataset['species'] if 'species' in dataset else ['rat']
        secondary_region = dataset['secondary_region'] if 'secondary_region' in dataset else None
        cell_type = dataset['cell_type'] if 'cell_type' in dataset else None
        try:
            page_url = f"{base_page_url}?instance={dataset['neuron_id']}&layer={secondary_region or ''}&mtype={cell_type or ''}"
            image_url = f"{base_image_url}/{dataset['neuron_id']}.jpeg"
            return {
                'identifier': storage_identifier,
                'source': {
                    'source_id': storage_identifier,
                    'id': str(dataset['neuron_id']),
                    'type': 'morphology',
                    'name': dataset['neuron_name'],
                    'page_link': page_url,
                    'icon': image_url,
                    'region': region,
                    'species': species,
                    'secondary_region': [secondary_region],
                    'cell_type': cell_type,
                    'source': self.source
                }
            }
        except Exception as ex:
            return None