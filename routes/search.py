import math
from flask import request, jsonify
from injector import Injector
from icecream import ic
from dependency import AppModule
from services import SearchService
from helpers.search_helper import parse_query_args
from . import routes_api


@routes_api.route('/search/<index_name>/all', methods=['POST', 'GET'])
def get_all(index_name):
    try:
        ids = []
        data = {}
        response = {}
        if request.method == 'POST':
            data = request.get_json()
        else:
            data = request.args.to_dict()
        if 'ids' in data and isinstance(data['ids'], str):
            data['ids'] = data['ids'].split(',')
        else:
            data['ids'] = []
        ids = data['ids'] if data['ids'] else []
        search_service = Injector(AppModule).get(SearchService)
        result = search_service.get_all_in_index(index_name, ids=ids)
        if result and 'hits' in result and 'hits' in result['hits']:
            response = {
                'items': [item['source'].to_dict() for item in result['hits']['hits']]
            }
        return response
    except Exception as ex:
        ic(f'Exception retrieving all from {index_name}')
        raise ex

@routes_api.route('/search/<index_name>', methods=['POST', 'GET'])
@routes_api.route('/search/<index_name>/<page>', methods=['POST', 'GET'])
@routes_api.route('/search/<index_name>/<page>/<hits_per_page>', methods=['POST', 'GET'])
def search(index_name, page=0, hits_per_page=20):
    try:
        data = {}
        if request.method == 'POST':
            data = request.get_json()
        else:
            data = request.args.to_dict()
        page = int(page)
        hits_per_page = int(hits_per_page)
        start = page * hits_per_page
        search_service = Injector(AppModule).get(SearchService)
        data_type, query, region, cell_type, species = parse_query_args(data)
        result = search_service.search_in_index(index_name, start, hits_per_page, data_type, query, [], region, cell_type, species)
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