from injector import inject
from helpers import ElasticStorage

fields = {
    'dataset': [('secondary_region', 'keyword')]
}

class FilterService:

    @inject
    def __init__(self, storage: ElasticStorage):
        self.storage = storage

    def filters(self, index_name):
        try:
            response = self.storage.get_terms_aggregation(fields[index_name])
            return response
        except Exception as ex:
            print(ex)
            raise ex