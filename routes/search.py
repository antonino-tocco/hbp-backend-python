import math
from flask import request
from injector import Injector
from . import routes_api
from services import SearchService


@routes_api.route('/search/<index_name>', methods=['POST'])
@routes_api.route('/search/<index_name>/<page>', methods=['POST'])
@routes_api.route('/search/<index_name>/<page>/<hits_per_page>', methods=['POST'])
def search(index_name, page=0, hits_per_page=20):
    try:
        data = request.get_json()
        page = int(page)
        hits_per_page = int(hits_per_page)
        start = page * hits_per_page
        search_service = Injector().get(SearchService)
        query = data['query']
        region = data['region']
        cell_type = data['cell_type']
        species = data['species']
        result = search_service.search_in_index(index_name, start, hits_per_page, query, region, cell_type, species)
        total_items = result['hits']['total']['value']
        total_page = math.ceil(total_items / hits_per_page)
        response = {
            'total': result['hits']['total']['value'],
            'total_page': total_page,
            'items': [item['_source'].to_dict() for item in result['hits']['hits']],
            'page': page,
            'size': hits_per_page
        }
        return response
    except Exception as ex:
        print(ex)
        return {
            'total': 0,
            'total_page': 1,
            'items': [],
            'page': page,
            'size': hits_per_page
        }