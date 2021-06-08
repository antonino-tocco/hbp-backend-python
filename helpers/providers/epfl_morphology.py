import os
import json
import logging
from icecream import ic
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, Q
from .provider import Provider

base_page_url = f'https://www.hippocampushub.eu/model/experimental-data/neuronal-morphology/'
base_image_url = f'https://www.hippocampushub.eu/model/assets/images/exp-morph-images/'

epfl_es_host = 'https://bbp.epfl.ch/nexus/v1/views/public/hippocampus-hub/'


class EpflMorphologyProvider(Provider):

    def __init__(self):
        super(EpflMorphologyProvider, self).__init__()
        self.id_prefix = 'internal'
        self.source = 'internal'
        self.index_name = ''
        self.es = Elasticsearch(hosts=[epfl_es_host])

    async def search_datasets(self, start=0, hits_per_page=50):
        results = []
        index_name = 'https://bbp.epfl.ch/neurosciencegraph/data/views/es/dataset'
        s = Search(using=self.es)
        s = s.index(index_name)
        try:
            s = s.filter('term', **{'_deprecated': False})
            #s = s.filter('bool', **{'@type': 'NeuronMorphology'})
            s = s.filter('term', **{'@type': 'NeuronMorphology'})
            s = s.extra(from_=0, size=1000)
            results = s.execute()
            return results
        except Exception as ex:
            ic(f'Exception make request {ex}')
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