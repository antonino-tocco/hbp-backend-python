from injector import inject
from helpers import ElasticStorage
from icecream import ic

default_fields = {
    'dataset': {
        'morphology': {
            'secondary_region': {
                'label': 'region',
                'type': 'multiple',
                'values': ('secondary_region', 'keyword'),
            },
            'cell_type': {
                'label': 'cell type',
                'type': 'multiple',
                'values': ('cell_type', 'keyword'),
            },
            'species': {
                'label': 'species',
                'type': 'multiple',
                'values': ('species', 'keyword')
            }
        },
        'electrophysiology': {
            'secondary_region': {
                'label': 'region',
                'type': 'multiple',
                'values': ('secondary_region', 'keyword'),
            },
        },
        'connection': {
            'pre': {
                'secondary_region': {
                    'label': 'region',
                    'type': 'multiple',
                    'values': ('pre.secondary_region', 'keyword'),
                },
            },
            'post': {
                'secondary_region': {
                    'label': 'region',
                    'type': 'multiple',
                    'values': ('post.secondary_region', 'keyword'),
                },
            }
        }
    },
    'model': {
        'channels': {
            'label': 'channels',
            'type': 'suggestion',
            'values': ('channels', 'keyword')
        },
        'receptors': {
            'label': 'receptors',
            'type': 'suggestion',
            'values': ('receptors', 'keyword')
        }
    }
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
                if fields is not None:
                    if data_type is not None and data_type in fields:
                        computed_fields = self.__extract_filter_values__(fields[data_type])
                    else:
                        computed_fields = self.__extract_filter_values__(fields)
            response = self.storage.get_terms_aggregation(index_name, data_type, fields=computed_fields)
            result = {}
            for key in response:
                ic(f'Key {key}')
                result[key] = {
                    'key': key,
                    'label': fields[key]['label'],
                    'type': fields[key]['type'],
                    'values': response[key]
                }
            return result
        except Exception as ex:
            ic(f'Exception getting filter {ex}')
            raise ex

    def __extract_filter_values__(self, fields, filters=[]):
        for key in fields:
            value = fields[key]
            if 'values' in value:
                filters.append(value['values'])
            else:
                filters = self.__extract_filter_values__(value, filters)
        return filters
