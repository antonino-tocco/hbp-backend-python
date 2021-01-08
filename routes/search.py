from injector import inject
from . import routes_api
from services import SearchService


@routes_api.route('/search/<index_name>', methods=['GET'])
@routes_api.route('/search/<index_name>/<start>/<hits_per_page>', methods=['GET'])
@inject(SearchService)
def search(search_service, index_name, start=0, hits_per_page=20):
    try:
        results = search_service.search_in_index(index_name, start, hits_per_page)
        return results
    except Exception as ex:
        print(ex)
        return []