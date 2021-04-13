from injector import inject
from helpers import ElasticStorage
from icecream import ic

default_fields = {
    'dataset': {
        'morphology': {
            'secondary_region': {
                'label': 'region',
                'type': 'multiple',
                'order': 2,
                'values': ('secondary_region', 'keyword'),
            },
            'cell_type': {
                'label': 'cell type',
                'type': 'multiple',
                'order': 3,
                'values': ('cell_type', 'keyword'),
            },
            'species': {
                'label': 'species',
                'type': 'multiple',
                'order': 1,
                'values': ('species', 'keyword')
            }
        },
        'electrophysiology': {
            'secondary_region': {
                'label': 'region',
                'type': 'multiple',
                'order': 1,
                'values': ('secondary_region', 'keyword'),
            },
            'layers': {
                'key': 'layers',
                'label': 'layers',
                'type': 'multiple',
                'order': 2,
                'depends_on': ['secondary_region'],
                'values': ('layers', 'keyword')
            }
        },
        'connection': {
            'presynaptic': {
                'order': 1,
                'secondary_region': {
                    'key': 'secondary_region',
                    'label': 'region',
                    'type': 'multiple',
                    'order': 1,
                    'values': ('presynaptic.secondary_region', 'keyword')
                },
                'layers': {
                    'key': 'layers',
                    'label': 'layers',
                    'type': 'multiple',
                    'order': 2,
                    'depends_on': ['presynaptic.secondary_region'],
                    'values': ('presynaptic.layers', 'keyword')
                }
            },
            'postsynaptic': {
                'order': 2,
                'secondary_region': {
                    'key': 'secondary_region',
                    'label': 'region',
                    'type': 'multiple',
                    'order': 1,
                    'values': ('postsynaptic.secondary_region', 'keyword')
                },
                'layers': {
                    'key': 'layers',
                    'label': 'layers',
                    'type': 'multiple',
                    'order': 2,
                    'depends_on': ['postsynaptic.secondary_region'],
                    'values': ('postsynaptic.layers', 'keyword')
                }
            }
        }
    },
    'model': {
        'cell_types': {
          'label': 'cell types',
          'type': 'multiple',
          'order': 1,
          'values': ('cell_types', 'keyword')
        },
        'channels': {
            'label': 'channels',
            'type': 'multiple',
            'order': 1,
            'values': ('channels', 'keyword')
        },
        'receptors': {
            'label': 'receptors',
            'type': 'multiple',
            'order': 2,
            'values': ('receptors', 'keyword')
        },
        'model_concepts': {
            'label': 'model concepts',
            'type': 'multiple',
            'order': 3,
            'values': ('model_concepts', 'keyword')
        },
        'implementers': {
            'label': 'implementers',
            'type': 'multiple',
            'order': 4,
            'values': ('implementers', 'keyword')
        }
    }
}


class FilterService:
    @inject
    def __init__(self, storage: ElasticStorage):
        self.storage = storage

    def types(self, index_name):
        result = {}
        try:
            response = self.storage.get_terms_aggregation(index_name, fields=[('type', 'keyword')])
            return {
                'label': 'type',
                'values': response['type']
            }
        except Exception as ex:
            ic(f'Exception getting data types {ex}')
        return result

    def filters(self, index_name, data_type=None, fields=None):
        result = {}
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
                                'order': fields[data_type][prefix_key]['order'] if data_type is not None else 0,
                                'items': {}
                            }
                        result[prefix_key]['items'][computed_key] = {
                            'key': computed_key,
                            'label': filter_data['label'],
                            'type': filter_data['type'],
                            'order': filter_data['order'],
                            'depends_on': filter_data['depends_on'] if 'depends_on' in filter_data else [],
                            'values': response[key]
                        }
                    else:
                        result[key] = {
                            'key': computed_key,
                            'label': filter_data['label'],
                            'type': filter_data['type'],
                            'order': filter_data['order'],
                            'depends_on': filter_data['depends_on'] if 'depends_on' in filter_data else [],
                            'values': response[key]
                        }
        except Exception as ex:
            ic(f'Exception getting filter {ex}')
            raise ex
        return result

    def __extract_filter_values__(self, fields, initial_filters=[]):
        filters = initial_filters.copy()
        for key in fields:
            if key != 'order':
                value = fields[key]
                if 'values' in value:
                    filters.append(value['values'])
                else:
                    filters = self.__extract_filter_values__(value, filters)
        return filters
