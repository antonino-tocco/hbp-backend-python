import os
import json
import logging
from icecream import ic
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, Q
from .provider import Provider

base_page_url = f'https://www.hippocampushub.eu/model/experimental-data/neuronal-morphology/'
base_image_url = f'https://www.hippocampushub.eu/model/assets/images/exp-morph-images/'

nexus_es_host = 'https://bbp.epfl.ch/nexus/v1/views/public/hippocampus-hub/'


class NexusMorphologyProvider(Provider):

    def __init__(self):
        super(NexusMorphologyProvider, self).__init__()
        self.id_prefix = 'internal_morphologies'
        self.source = 'INTERNAL'
        self.index_name = 'https://bbp.epfl.ch/neurosciencegraph/data/views/es/dataset'
        self.es = Elasticsearch(hosts=[nexus_es_host])

    async def search_datasets(self, start=0, hits_per_page=50):
        results = []
        s = Search(using=self.es)
        s = s.index(self.index_name)
        try:
            s = s.filter('term', **{'_deprecated': False})
            #s = s.filter('bool', **{'@type': 'NeuronMorphology'})
            s = s.filter('term', **{'@type': 'NeuronMorphology'})
            s = s.extra(from_=0, size=1000)
            results = s.execute()
            return self.map_datasets(results)
        except Exception as ex:
            ic(f'Exception make request {ex}')
        return results

    def map_datasets(self, items=[]):
        try:
            all_items = [self.__map__item__(item) for item in items]
            all_items = list(filter(lambda x: x is not None, all_items))
            return all_items
        except Exception as ex:
            ic(f'Exception mapping datasets {ex}')
            return []

    def __map__item__(self, dataset):
        storage_identifier = f"{self.id_prefix}-{dataset['@id']}"
        region = dataset['region'] if 'region' in dataset else 'hippocampus'
        species = dataset['species'] if 'species' in dataset else ['rat']
        secondary_region = None
        cell_type = None
        if 'brainLocation' in dataset and 'brainRegion' in dataset['brainLocation'] and 'label' in dataset['brainLocation']['brainRegion']:
            secondary_region = dataset['brainLocation']['brainRegion']['label']
        if 'annotation' in dataset and 'hasBody' in dataset['annotation'] and 'label' in dataset['annotation']['hasBody']:
            cell_type = dataset['annotation']['hasBody']['label']
        try:
            page_url = f"{base_page_url}?instance={dataset['name']}&layer={secondary_region or ''}&mtype={cell_type or ''}#data"
            image_url = f"{base_image_url}/{dataset['name']}.jpeg"
            papers = [{
                'label': dataset['url'],
                'url': dataset['url']
            }] if 'url' in dataset and dataset['url'] is not None else []
            return {
                'identifier': storage_identifier,
                'source': {
                    'source_id': storage_identifier,
                    'id': str(dataset['@id']),
                    'type': 'morphology',
                    'name': dataset['name'],
                    'page_link': page_url,
                    'icon': image_url,
                    'region': region,
                    'species': species,
                    'secondary_region': [secondary_region],
                    'cell_type': cell_type,
                    'papers': papers,
                    'source': self.source
                }
            }
        except Exception as ex:
            ic(f'Exception mapping datasets {ex}')
            return None