from injector import inject
from helpers import ElasticStorage
from icecream import ic

default_fields = {
    'dataset': {
        'morphology': {
            'secondary_region': {
                'label': 'region',
                'values': ('secondary_region', 'keyword'),
            },
            'cell_type': {
                'label': 'cell type',
                'values': ('cell_type', 'keyword'),
            },
            'species': {
                'label': 'species',
                'values': ('species', 'keyword')
            }
        },
        'electrophysiology': {},
        'connections': {}
    },
    'model': {}
}


class FilterService:
    @inject
    def __init__(self, storage: ElasticStorage):
        self.storage = storage

    def types(self, index_name):
        try:
            response = self.storage.get_terms_aggregation(index_name, fields=[('type', 'keyword')])
            return {
                'label': 'type',
                'values': response['type']
            }
        except Exception as ex:
            ic(f'Exception getting data types {ex}')
            raise ex

    def filters(self, index_name, data_type=None, fields=None):
        try:
            computed_fields = fields
            if fields is None:
                fields = default_fields[index_name]
                if fields is not None and data_type in fields:
                    computed_fields = []
                    fields = fields[data_type]
                    for key in fields:
                        computed_fields.append(fields[key]['values'])
            response = self.storage.get_terms_aggregation(index_name, data_type, fields=computed_fields)
            result = {}
            for key in response:
                ic(f'Key {key}')
                result[key] = {
                    'key': key,
                    'label': fields[key]['label'],
                    'values': response[key]
                }
            return result
        except Exception as ex:
            ic(f'Exception getting filter {ex}')
            raise ex
