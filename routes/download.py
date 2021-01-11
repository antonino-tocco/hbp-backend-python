from . import routes_api
from flask import request
from injector import Injector
from services import SearchService

@routes_api.route('/download/<index_name>')
def download(index_name):
    try:
        data = request.get_json()
        search_service = Injector().get(SearchService)
        ids = data['ids']
        results = search_service.get_all_in_index(index_name, ids=ids)
        return results
    except Exception as ex:
        print(ex)


@routes_api.route('/download/<index_name>/all')
def download_all(index_name):
    try:
        data = request.get_json()
        search_service = Injector().get(SearchService)
        query = data['query']
        region = data['region']
        cell_type = data['cell_type']
        species = data['species']
        results = search_service.get_all_in_index(index_name, query=query, secondary_region=region, cell_type=cell_type, species=species)
        return results
    except Exception as ex:
        print(ex)