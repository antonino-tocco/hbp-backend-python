import os
import logging
import requests
from .provider import Provider
from hbp_validation_framework import ModelCatalog
#from hbp_dataset_dataset.hbp_dataset_dataset import Hbp_datasetDataset
#from kgquery.queryApi import KGClient
from icecream import ic
import json
from jsbeautifier import beautify

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
        self.model_catalog = ModelCatalog(token=self.token)
        #self.client = KGClient.by_single_token(os.getenv('HBP_AUTH_TOKEN'), "https://kg.humanbrainproject.eu/query").released()
        self.id_prefix = 'knowledge'
        self.source = 'Knowledge'

    # async def search_datasets(self, start=0, hits_per_page=50):
    #     try:
    #         query = Hbp_datasetDataset(self.client)
    #         all_data = query.fetch(size=100)
    #         if all_data is None:
    #             all_data = []
    #         while query.has_more_items():
    #             print(f'Get items page')
    #             data = query.next_page()
    #             all_data.extend(data)
    #         return self.map_datasets(all_data)
    #     except Exception as ex:
    #         ic(f"Exception searching datasets {ex}")
    #         return []

    async def search_models(self, start=0, hits_per_page=50):
        try:
            models = self.model_catalog.list_models(brain_region='hippocampus')
            #self.__generate_html_report__(models)
            return self.map_models(models)
        except Exception as ex:
            ic(f"Exception searching models {ex}")
            return []

    def map_datasets(self, items=[]):
        try:
            mapped_datasets = [self.__map_dataset__(x) for x in items]
            return mapped_datasets
        except Exception as ex:
            ic(ex)
            raise ex

    def map_models(self, items=[]):
        try:
            mapped_models = [self.__map_model__(x) for x in items]
            return mapped_models
        except Exception as ex:
            ic(ex)
            raise ex

    def __generate_html_report__(self, models=[]):
        with open('knowledge.html', 'w') as f:
            f.write('<html><head></head><body>')
            f.write('<h1>Knowledge Results</h1>')
            for model in models:
                links = []
                model['description'] = None
                if 'instances' is not model and model['instances'] is not None and len(model['instances']) > 0:
                    links = [x['source'] for x in model['instances']]
                f.write(f"<p>{model['name']} <br/><br /> {beautify(json.dumps(model, indent=4, sort_keys=True))} <br/><br/>")
                for link in links:
                    f.write(f"Link to model: <a href='{link}'>{link}</a>")
                f.write("</p>")
            f.write('</body></html>')
            f.close()

    def __map_dataset__(self, item):
        brain_region = 'hippocampal'
        if hasattr(item, 'region'):
            brain_region = item.region
        secondary_region = ''
        if hasattr(item, 'secondary_region'):
            secondary_region = item.secondary_region
        return {
            'id': item.id,
            'name': item.name,
            'data_descriptor': item.data_descriptor,
            'description': item.description,
            'modalities': [modality.name for modality in item.modality],
            'owners': [owner.name for owner in item.owners],
            'brain_region': brain_region,
            #'keywords': [protocol.name for protocol in dataset.protocols],
            #'methods': [method.name for method in dataset.methods],
            'files': [{
                'name': x.name,
                'file_size': x.file_size,
                'url': x.url
            } for x in item.files]
        }


    def __map_model__(self, item):
        assert(item is not None)
        try:
            storage_identifier = f"{self.id_prefix}-{item['id']}"
            cell_types = []
            species = []
            model_scopes = []
            if 'cell_type' in item and item['cell_type'] is not None:
                cell_types = [item['cell_type']]
            if 'species' in item and item['species'] is not None:
                species = item['species'].split(',')
            if 'model_scope' in item and item['model_scope'] is not None:
                model_scopes = item['model_scope'].split(',')

            return {
                'identifier': storage_identifier,
                'source': {
                    'source_id': storage_identifier,
                    'id': item['id'],
                    'name': item['name'],
                    'cell_types': cell_types,
                    'brain_region': item['brain_region'],
                    'species': species,
                    'page_link': '',
                    'download_link': '',
                    'model_scope': model_scopes,
                    'source': self.source
                }
            }
        except Exception as ex:
            ic(ex)
            raise ex



