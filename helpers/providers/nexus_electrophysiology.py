import logging
import urllib
from icecream import ic
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, Q
from helpers.download_helper import download_image
from .provider import Provider

base_page_url = f'https://www.hippocampushub.eu/model/experimental-data/neuronal-electrophysiology/'
base_image_url = f'https://www.hippocampushub.eu/model/assets/images/exp-morph-images/'

nexus_es_host = 'https://bbp.epfl.ch/nexus/v1/views/public/hippocampus-hub/'

logging.basicConfig(filename='es_search.log', level=logging.DEBUG)


class NexusElectrophysiologyProvider(Provider):

    def __init__(self):
        super(NexusElectrophysiologyProvider, self).__init__()
        self.id_prefix = 'internal_electrophysiologies'
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
            s = s.filter('term', **{'@type': 'Trace'})
            s = s.query(Q('nested', path='distribution', query=Q('bool', must=[Q('match', **{'distribution.encodingFormat':'application/nwb'})])))
            s = s.extra(from_=0, size=1000)
            results = s.execute()
            return await self.map_datasets(results)
        except Exception as ex:
            ic(f'Exception make request {ex}')
        return results

    async def map_datasets(self, response=None):
        try:
            _all_items = [item for item in response]
            #json_response = json.dumps(response.to_dict())
            #with open('electrophysiology.json', 'w') as file:
            #    file.write(json_response)
            #    file.close()
            all_items = [await self.__map__item__(item) for item in _all_items]
            all_items = list(filter(lambda x: x is not None, all_items))
            # with open('electrophysiology.json', 'w') as file:
            #     json_items = list(map(lambda x: {
            #         'name': x['source']['name'] if 'name' in x['source'] else None,
            #         'download_link': x['source']['download_link'] if 'download_link' in x['source'] else None
            #     }, all_items))
            #
            #     file.write(json.dumps(json_items))
            #     file.close()
            return all_items
        except Exception as ex:
            ic(f'Exception mapping datasets {ex}')
            return []

    async def __map__item__(self, dataset):
        storage_identifier = f"{self.id_prefix}-{dataset['@id']}"
        region = dataset['region'] if 'region' in dataset else 'hippocampus'
        species = dataset['species'] if 'species' in dataset else ['rat']
        secondary_region = None
        etype = None
        original_image_url = None
        image_url = None
        computed_secondary_region = None
        download_link = None
        name = dataset['name']
        metadata_url = f'https://object.cscs.ch/v1/AUTH_c0a333ecf7c045809321ce9d9ecdfdea/web-resources-bsp/data/NFE/MetadataHippocampusHub/{name}_metadata.json'
        try:
            if 'brainLocation' in dataset and 'brainRegion' in dataset['brainLocation'] and 'label' in \
                    dataset['brainLocation']['brainRegion']:
                secondary_region = dataset['brainLocation']['brainRegion']['label']
            if 'annotation' in dataset and 'hasBody' in dataset['annotation'] and 'label' in dataset['annotation']['hasBody']:
                etype = dataset['annotation']['hasBody']['label']
            if 'distribution' in dataset and dataset['distribution'] is not None:
                distribution = dataset['distribution']
                for download_url in distribution:
                    url = download_url['contentUrl'] if 'contentUrl' in download_url and \
                        'encodingFormat' in download_url and download_url['encodingFormat'] == 'application/abf' \
                        else None
                    if url is not None:
                        download_link = url
                        break

            computed_secondary_region = secondary_region.split('_')[0] if secondary_region is not None else None
            if etype is None:
                return None
            page_url = f"{base_page_url}?etype_instance={dataset['name']}&layer={computed_secondary_region or ''}&etype={etype or ''}#data"
            if 'image' in dataset and dataset['image'] is not None:
                for image in dataset['image']:
                    if image['about'] == 'nsg:ResponseTrace':
                        original_image_url = f"{image['@id']}"
                        break
                if original_image_url is None:
                    original_image_url = f"{dataset['image'][0]['@id']}"
                if original_image_url is not None:
                    image_url = f"https://bbp.epfl.ch/nexus/v1/resources/public/hippocampus-hub/_/{urllib.parse.quote_plus(original_image_url)}"
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
                    'layers': [],
                    'download_link': download_link,
                    'cell_type': None,
                    'etype': etype,
                    'papers': papers,
                    'source': self.source,
                    'metadata': {
                        'url': metadata_url
                    }
                }
            }
        except Exception as ex:
            ic(f'Exception mapping datasets {ex}')
            return None