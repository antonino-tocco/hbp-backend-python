from injector import Injector
from dependency import AppModule
from services import FilterService
from . import routes_api


@routes_api.route('/filters/<index_name>')
def filters(index_name):
    try:
        filter_service = Injector(AppModule).get(FilterService)
        response = filter_service.filters(index_name)
        return response
    except Exception as ex:
        print(ex)