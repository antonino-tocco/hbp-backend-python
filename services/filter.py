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
            'layers': {
                'key': 'layers',
                'label': 'layers',
                'type': 'multiple',
                'depends_on': 'secondary_region',
                'values': ('layers', 'keyword')
            }
        },
        'connection': {
            'presynaptic': {
                'secondary_region': {
                    'key': 'secondary_region',
                    'label': 'region',
                    'type': 'multiple',
                    'values': ('presynaptic.secondary_region', 'keyword')
                },
                'layers': {
                    'key': 'layers',
                    'label': 'layers',
                    'type': 'multiple',
                    'depends_on': 'presynaptic.secondary_region',
                    'values': ('presynaptic.layers', 'keyword')
                }
            },
            'postsynaptic': {
                'secondary_region': {
                    'key': 'secondary_region',
                    'label': 'region',
                    'type': 'multiple',
                    'values': ('postsynaptic.secondary_region', 'keyword')
                },
                'layers': {
                    'key': 'layers',
                    'label': 'layers',
                    'type': 'multiple',
                    'depends_on': 'postsynaptic.secondary_region',
                    'values': ('presynaptic.layers', 'keyword')
                }
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
                        computed_fields = self.__extract_filter_values__(fields[data_type], [])
                    else:
                        computed_fields = self.__extract_filter_values__(fields, [])
            response = self.storage.get_terms_aggregation(index_name, data_type, fields=computed_fields)
            result = {}
            for key in response:
                prefix_key = key.split('.')[0]
                computed_key = key.split('.')[-1]
                if data_type is not None:
                    filter_data = fields[data_type][prefix_key][computed_key] if prefix_key != computed_key else \
                        fields[data_type][computed_key]
                else:
                    filter_data = fields[prefix_key][computed_key] if prefix_key != computed_key else \
                        fields[computed_key]
                ic(f'Key {key}')
                if prefix_key != computed_key:
                    if prefix_key not in result:
                        result[prefix_key] = {
                            'label': prefix_key,
                            'items': {}
                        }
                    result[prefix_key]['items'][computed_key] = {
                        'key': computed_key,
                        'label': filter_data['label'],
                        'type': filter_data['type'],
                        'values': response[key]
                    }
                else:
                    result[key] = {
                        'key': computed_key,
                        'label': filter_data['label'],
                        'type': filter_data['type'],
                        'values': response[key]
                    }
            return result
        except Exception as ex:
            ic(f'Exception getting filter {ex}')
            raise ex

    def __extract_filter_values__(self, fields, initial_filters=[]):
        filters = initial_filters.copy()
        for key in fields:
            value = fields[key]
            if 'values' in value:
                filters.append(value['values'])
            else:
                filters = self.__extract_filter_values__(value, filters)
        return filters
