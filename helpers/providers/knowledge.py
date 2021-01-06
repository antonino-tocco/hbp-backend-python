import os
from . import Provider
from kgquery.queryApi import KGClient
from hbp_dataset_dataset.hbp_dataset_dataset import Hbp_datasetDataset


class KnowledgeProvider(Provider):

    def __init__(self):
        super(KnowledgeProvider, self).__init__()
        self.client = KGClient.by_single_token(os.getenv('HBP_AUTH_TOKEN'), "https://kg.humanbrainproject.eu/query")

    def search(self, query_text='', hits_per_page=20):
        try:
            query = Hbp_datasetDataset(self.client)
            data = query.fetch()
            print(f'Query result {data}')
        except Exception as ex:
            print(ex)

    def map_items(self):
        return []

