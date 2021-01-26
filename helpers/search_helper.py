def parse_query_args(data=None):
    data_type = None
    query = ''
    region = ''
    cell_type = ''
    species = ''
    if data is None:
        return data_type, query, region, cell_type, species
    if 'data_type' in data:
        data_type = data['data_type']
    if 'query' in data:
        query = data['query']
    if 'region' in data:
        region = data['region']
    if 'cell_type' in data:
        cell_type = data['cell_type']
    if 'species' in data:
        species = data['species']
    return data_type, query, region, cell_type, species