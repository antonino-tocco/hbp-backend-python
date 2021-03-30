def parse_query_args(data=None):
    data_type = None
    query, region, cell_type, species, layers, channels, receptors, implementers, model_concepts = \
        '', '', '', '', '', '', '', '', ''
    if data is None:
        return data_type, query, region, cell_type, species
    if 'data_type' in data:
        data_type = data['data_type']
    filters = {}
    if 'query' in data:
        query = data['query']
    if 'filters' in data and data['filters']:
        filters = data['filters']
        if 'secondary_region' in filters:
            region = filters['secondary_region']
        if 'cell_type' in filters:
            cell_type = filters['cell_type']
        if 'species' in filters:
            species = filters['species']
        if 'channels' in filters:
            channels = filters['channels']
        if 'receptors' in filters:
            receptors = filters['receptors']
        if 'layers' in filters:
            layers = filters['layers']
        if 'implementers' in filters:
            implementers = filters['implementers']
        if 'model_concepts' in filters:
            model_concepts = filters['model_concepts']
    return data_type, query, region, cell_type, species, layers, channels, receptors, implementers, model_concepts


def parse_connections_args(data=None):
    query = ''
    presynaptic = {}
    postsynaptic = {}
    filters = {}
    if data is None:
        return query, presynaptic, postsynaptic
    else:
        if 'filters' in data and data['filters']:
            filters = data['filters']
            if 'query' in filters:
                query = filters
            if 'presynaptic' in filters:
                presynaptic = filters['presynaptic']
            if 'postsynaptic' in filters:
                postsynaptic = filters['postsynaptic']
    return query, presynaptic, postsynaptic