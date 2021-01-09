import os
from . import enabled_providers
from . import ElasticStorage

es = ElasticStorage(host=os.getenv('ELASTIC_SEARCH_URL'))

async def import_data():
    for provider in enabled_providers:
        datasets = provider.search()
        for dataset in datasets:
            print(dataset['name'])
            es.store_object('dataset', dataset['id'], dataset)
