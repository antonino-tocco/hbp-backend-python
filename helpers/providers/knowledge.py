import os
import logging
import requests
from urllib.parse import urlparse, quote_plus, parse_qs, urlencode
from fairgraph import KGClient
from fairgraph.base import KGQuery
from fairgraph.minds import Dataset, Modality
#from kgquery.queryApi import KGClient
from hbp_dataset_dataset.hbp_dataset_dataset import Hbp_datasetDataset
from . import Provider

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
        self.client = KGClient(self.token)
        self.session = requests.session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}'
        })
        #self.client = KGClient.by_single_token(os.getenv('HBP_AUTH_TOKEN'), "https://kg.humanbrainproject.eu/query")

    def search(self, query_text='hippocampal', hits_per_page=20):
        #url = f"{BASE_URL}{ENPOINTS['search']('public')}"
        try:
            query = {
                "path": "minds:subjects / minds:samples / minds:methods / schema:name / schema:modality",
                "op": "eq",
                "value": query_text
            }
            context = {
                "schema": "http://schema.org/",
                "minds": "https://schema.hbp.eu/minds/"
            }
            #query = Hbp_datasetDataset(self.client)
            #data = query.fetch(size=20)
            activity_datasets = Dataset.list(self.client, filters=query)
            return self.map_datasets(activity_datasets)
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
        return {
            'id': dataset.identifier,
            'name': dataset.name,
            'citation': dataset.citation,
            'dataDescriptor': dataset.dataDescriptor.url,
            'regions': dataset.region,
            'description': dataset.description,
            'modalities': [modality.resolve(self.client) for modality in dataset.modality],
            'preparations': [dataset.preparations],
            'owners': dataset.owners.resolve(self.client),
            'contributors': [contributor.resolve(self.client) for contributor in dataset.contributors],
            'license': dataset.license,
            'files': []
        }



