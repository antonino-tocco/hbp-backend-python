import math
from flask import request, jsonify
from injector import Injector
from icecream import ic
from dependency import AppModule
from services import SearchService
from helpers.search_helper import parse_query_args, parse_connections_args
from . import routes_api


def search_connections(index_name, page, hits_per_page, data):
    try:
        page = int(page)
        hits_per_page = int(hits_per_page)
        start = page * hits_per_page
        search_service = Injector(AppModule).get(SearchService)
        query, presynaptic, postsynaptic = parse_connections_args(data)
        result = search_service.search_connections(start, hits_per_page, query, presynaptic, postsynaptic)
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
        ic(ex)
        return {
            'total': 0,
            'total_page': 1,
            'items': [],
            'page': page,
            'size': hits_per_page
        }


def search_for_index(index_name, page, hits_per_page, data):
    try:
        page = int(page)
        hits_per_page = int(hits_per_page)
        start = page * hits_per_page
        search_service = Injector(AppModule).get(SearchService)
        data_type, query, region, cell_type, species, layers, channels, receptors, implementers, model_concepts = parse_query_args(data)
        result = search_service.search_in_index(index_name, start, hits_per_page, data_type, query, region,
                                                cell_type, species, layers, channels, receptors, implementers, model_concepts)
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
        ic(ex)
        return {
            'total': 0,
            'total_page': 1,
            'items': [],
            'page': page,
            'size': hits_per_page
        }


search_methods_map = {
    'connection': search_connections,
    'default': search_for_index
}


@routes_api.route('/search/<index_name>/all', methods=['POST'])
def get_all(index_name):
    """
    Search for all the resources in the storage
    ---
    tags:
      - Search all
    parameters:
      - in: path
        name: index_name
        type: string
        example: dataset
      - in: body
        name: body
        schema:
          id: SearchAllPayload
          properties:
            ids:
              type: array
              items:
                type: string
                description: The ids of the resources to search
    responses:
      200:
        description: 'OK'
    """
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
        if result:
            response = {
                'items': [item for item in result]
            }
        return response
    except Exception as ex:
        ic(f'Exception retrieving all from {index_name}')
        raise ex


@routes_api.route('/search/<index_name>', methods=['POST'])
@routes_api.route('/search/<index_name>/<page>', methods=['POST'])
@routes_api.route('/search/<index_name>/<page>/<hits_per_page>', methods=['POST'])
def search(index_name, page=0, hits_per_page=20):
    """
    Search for resources in storage
    ---
    tags:
      - Paged search
    parameters:
      - in: path
        name: index_name
        type: string
        example: dataset
        required: true
      - in: path
        name: page
        type: number
        example: 0
      - in: path
        name: hits_per_page
        type: number
        example: 20
      - in: body
        name: body
        schema:
          id: SearchPayload
          properties:
            data_type:
              type: string
              description: The data type of data
              example: morphology
            query:
              type: string
              description: The query for search
              example: 'abcdefg'
            filters:
              type: object
              properties:
                secondary_region:
                  type: string
                  description: The secondary region of the hippocampus to search. (only for morphologies and electrophysiologies)
                  example: CA1
                cell_type:
                  type: string
                  description: The cell type to search
                  example: principal cell
                species:
                  type: string
                  description: The species to search
                  example: rat, mouse
                channels:
                  type: string
                  description: The channel to search. (only for models)
                  example: I K
                receptors:
                  type: string
                  description: The receptor to search. (only for models)
                  example: AMPA
                layers:
                  type: string
                  description: The layer to search. (only for models)
                  example: CA1:SO
                implementers:
                  type: string
                  description: The implementers of the model. (only for models)
                  example: Migliore
                model_concepts:
                  type: string
                  description: The model concept to search. (only for models)
                  example: Detailed Neuronal Model

    responses:
      200:
        description: 'OK'
    """
    try:
        data = {}
        if request.method == 'POST':
            data = request.get_json()
        else:
            data = request.args.to_dict()
        data_type = data['data_type'] if 'data_type' in data else None
        if data_type is not None:
            search_method = search_methods_map[data_type] if data_type in search_methods_map else search_methods_map['default']
        else:
            search_method = search_methods_map['default']
        return search_method(index_name, page, hits_per_page, data)
    except Exception as ex:
        ic(f'Exception on search {ex}')
        return {
            'total': 0,
            'total_page': 1,
            'items': [],
            'page': page,
            'size': hits_per_page
        }