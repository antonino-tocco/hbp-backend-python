from injector import inject
from helpers import ElasticStorage

default_fields = {
    'dataset': [('secondary_region', 'keyword'), ('cell_type', 'keyword'), ('species', 'keyword')],
    'model': []
}


class FilterService:
    @inject
    def __init__(self, storage: ElasticStorage):
        self.storage = storage

    def filters(self, index_name, fields=None):
        try:
            if fields is None:
                fields = default_fields[index_name]
            response = self.storage.get_terms_aggregation(index_name, fields)
            return response
        except Exception as ex:
            print(ex)
            raise ex