import os
import json
import logging
from icecream import ic
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, Q
from .provider import Provider

base_page_url = f'https://www.hippocampushub.eu/model/experimental-data/neuronal-electrophysiology/'
base_image_url = f'https://www.hippocampushub.eu/model/assets/images/exp-morph-images/'

nexus_es_host = 'https://bbp.epfl.ch/nexus/v1/views/public/hippocampus-hub/'


class NexusElectrophysiologyProvider(Provider):

    def __init__(self):
        super(NexusElectrophysiologyProvider, self).__init__()
        self.id_prefix = 'epfl_electrophysiology'
        self.source = 'EPFL'
        self.index_name = 'https://bbp.epfl.ch/neurosciencegraph/data/views/es/dataset'
        self.es = Elasticsearch(hosts=[nexus_es_host])

    async def search_datasets(self, start=0, hits_per_page=50):
        results = []
        s = Search(using=self.es)
        s = s.index(self.index_name)
        try:
            s = s.filter('term', **{'_deprecated': False})
            #s = s.filter('bool', **{'@type': 'NeuronMorphology'})
            s = s.filter('term', **{'@type': 'Trace'})
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
        image_url = None
        computed_secondary_region = None
        download_link = None
        try:
            if 'brainLocation' in dataset and 'brainRegion' in dataset['brainLocation'] and 'label' in \
                    dataset['brainLocation']['brainRegion']:
                secondary_region = dataset['brainLocation']['brainRegion']['label']
            if 'annotation' in dataset and 'hasBody' in dataset['annotation'] and 'label' in dataset['annotation']['hasBody']:
                cell_type = dataset['annotation']['hasBody']['label']
            if 'distribution' in dataset and dataset['distribution'] is not None\
                    and dataset['distribution'] is list and len(dataset['distribution']) > 0:
                distribution = dataset['distribution']
                for download_url in distribution:
                    url = download_url['contentUrl'] if 'contentUrl' in download_url and \
                        'encodingFormat' in download_url and download_url['encodingFormat'] == 'application/abf' else None
                    if url is not None:
                        download_link = url
                        break

            computed_secondary_region = secondary_region.split('_')[0] if secondary_region is not None else None
            if cell_type is None:
                return None
            page_url = f"{base_page_url}?etype_instance={dataset['name']}&layer={computed_secondary_region or ''}&etype={cell_type or ''}"
            if 'image' in dataset and dataset['image'] is not None\
                    and dataset['image'] is list and len(dataset['image']) > 0:
                    image_url = dataset['image'][0]['@id']
            papers = [{
                'label': dataset['url'],
                'url': dataset['url']
            }] if 'url' in dataset and dataset['url'] is not None else []
            return {
                'identifier': storage_identifier,
                'source': {
                    'source_id': storage_identifier,
                    'id': str(dataset['@id']),
                    'type': 'electrophysiology',
                    'name': dataset['name'],
                    'page_link': page_url,
                    'icon': image_url,
                    'region': region,
                    'species': species,
                    'secondary_region': [computed_secondary_region] if computed_secondary_region is not None else [],
                    'layers': [cell_type] if cell_type is not None else [],
                    'download_link': download_link,
                    'cell_type': cell_type,
                    'papers': papers,
                    'source': self.source
                }
            }
        except Exception as ex:
            ic(f'Exception mapping datasets {ex}')
            return None