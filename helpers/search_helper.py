def parse_query_args(data=None):
    query = ''
    region = ''
    cell_type = ''
    species = ''
    if data is None:
        return query, region, cell_type, species
    if 'query' in data:
        query = data['query']
    if 'region' in data:
        region = data['region']
    if 'cell_type' in data:
        cell_type = data['cell_type']
    if 'species' in data:
        species = data['species']
    return query, region, cell_type, species