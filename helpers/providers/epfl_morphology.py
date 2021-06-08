import os
import json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, Q
from .provider import Provider

base_page_url = f'https://www.hippocampushub.eu/model/experimental-data/neuronal-morphology/'
base_image_url = f'https://www.hippocampushub.eu/model/assets/images/exp-morph-images/'

epfl_es_host = 'https://bbp.epfl.ch/nexus/v1/views/public/hippocampus-hub/'

elasticsearch = Elasticsearch(hosts=[epfl_es_host])


class InternalMorphologyProvider(Provider):

    def __init__(self):
        super(InternalMorphologyProvider, self).__init__()
        self.id_prefix = 'internal'
        self.source = 'internal'
        self.index_name = ''
        self.es = Elasticsearch(hosts=[epfl_es_host])

    async def search_datasets(self, start=0, hits_per_page=50):
        index_name = 'https%3A%2F%2Fbbp.epfl.ch%2Fneurosciencegraph%2Fdata%2Fviews%2Fes%2Fdataset'
        es_search = Search(using=self.es)
        es_search = es_search.index(index_name)
        try:
            es_search.filter('term', **{'_deprectated.keyword': False})
            es_search.filter('term', **{'type.keyword': 'NeuroMorphology'})
            results = es_search.execute()
            return results
        except Exception as ex:
            print(ex)
        return results

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