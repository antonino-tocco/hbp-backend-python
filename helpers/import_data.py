import os
from . import enabled_providers
from . import ElasticStorage

es = ElasticStorage(host=os.getenv('ELASTIC_SEARCH_URL'))


def import_data():
    print(f"*****************")
    print(f"IMPORT DATA")
    print(f"*****************")
    try:
        for provider in enabled_providers:
            datasets = provider.search()
            for dataset in datasets:
                print(dataset['name'])
                es.store_object('dataset', dataset['id'], dataset)
    except Exception as ex:
        print(f"*****************")
        print(f"IMPORT DATA EXCEPTION {ex}")
        print(f"*****************")
        raise ex
