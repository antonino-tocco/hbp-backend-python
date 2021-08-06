from injector import Injector
from icecream import ic
from dependency import AppModule
from services import FilterService
from . import routes_api


@routes_api.route('/types/<index_name>')
def types(index_name):
    try:
        filter_service = Injector(AppModule).get(FilterService)
        response = filter_service.types(index_name)
        return response
    except Exception as ex:
        ic(ex)
        raise ex


@routes_api.route('/filters/<index_name>')
@routes_api.route('/filters/<index_name>/<type>')
def filters(index_name, type=None):
    try:
        filter_service = Injector(AppModule).get(FilterService)
        response = filter_service.filters(index_name, data_type=type)
        return response
    except Exception as ex:
        ic(f'Exception on getting filters values {ex}')
        raise ex
