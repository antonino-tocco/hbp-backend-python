import os
import logging
import requests
from .provider import Provider
from hbp_dataset_dataset.hbp_dataset_dataset import Hbp_datasetDataset
from kgquery.queryApi import KGClient

BASE_URL = "https://search.kg.ebrains.eu"
ENPOINTS = {
    'definition': '/api/labels',
    'groups': '/api/groups',
    'search': lambda group: f'/api/search/{group}/search'
}

logger = logging.Logger('logger', level=logging.ERROR)

class KnowledgeProvider(Provider):

    def __init__(self):
        super(KnowledgeProvider, self).__init__()
        self.token = os.getenv('HBP_AUTH_TOKEN')
        self.session = requests.session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}'
        })
        self.client = KGClient.by_single_token(os.getenv('HBP_AUTH_TOKEN'), "https://kg.humanbrainproject.eu/query").released()

    def search(self, start = 0, hits_per_page=20):
        #url = f"{BASE_URL}{ENPOINTS['search']('public')}"
        try:
            query = {
                "path": "minds:subjects / minds:samples / minds:methods / schema:name / schema:modality",
                "op": "eq",
                "value": 'hippocampal'
            }
            context = {
                "schema": "http://schema.org/",
                "minds": "https://schema.hbp.eu/minds/"
            }
            query = Hbp_datasetDataset(self.client)
            all_data = query.fetch(size=100)
            while query.has_more_items():
                print(f'Get items page')
                data = query.next_page()
                all_data.extend(data)
            return self.map_datasets(all_data)
        except Exception as ex:
            print(ex)
            logger.exception(ex)
            return []

    def map_datasets(self, datasets=[]):
        try:
            mapped_datasets = [self.__map_dataset__(x) for x in datasets]
            return mapped_datasets
        except Exception as ex:
            print(ex)
            raise ex

    def __map_dataset__(self, dataset):
        #parts = urlparse(dataset.container_url)
        #query_dict = parse_qs(parts.query)
        #query_dict['format'] = "json"
        #url = parts._replace(query=urlencode(query_dict, True)).geturl()
        #response = self.session.get(url)
        #if response.status_code not in (200, 204):
        #    raise IOError(
        #        f"Unable to download dataset. Response code {response.status_code}")
        #contents = response.json()
        brain_region = 'hippocampal'
        if hasattr(dataset, 'region'):
            brain_region = dataset.region
        secondary_region = ''
        if hasattr(dataset, 'secondary_region'):
            secondary_region = dataset.secondary_region
        return {
            'id': dataset.id,
            'name': dataset.name,
            'data_descriptor': dataset.data_descriptor,
            'description': dataset.description,
            'modalities': [modality.name for modality in dataset.modality],
            'owners': [owner.name for owner in dataset.owners],
            'brain_region': brain_region,
            #'keywords': [protocol.name for protocol in dataset.protocols],
            #'methods': [method.name for method in dataset.methods],
            'files': [{
                'name': x.name,
                'file_size': x.file_size,
                'url': x.url
            } for x in dataset.files]
        }



