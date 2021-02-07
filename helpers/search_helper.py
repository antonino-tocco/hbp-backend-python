def parse_query_args(data=None):
    data_type = None
    query = ''
    region = ''
    cell_type = ''
    species = ''
    channels = ''
    receptors = ''
    if data is None:
        return data_type, query, region, cell_type, species
    if 'data_type' in data:
        data_type = data['data_type']
    filters = {}
    if 'filters' in data and data['filters']:
        filters = data['filters']
        if 'query' in filters:
            query = filters['query']
        if 'region' in filters:
            region = filters['region']
        if 'cell_type' in filters:
            cell_type = filters['cell_type']
        if 'species' in filters:
            species = filters['species']
        if 'channels' in filters:
            channels = filters['channels']
        if 'receptors' in filters:
            receptors = filters['receptors']
    return data_type, query, region, cell_type, species, channels, receptors