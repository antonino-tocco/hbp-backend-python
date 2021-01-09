from injector import Injector
from . import routes_api
from services import SearchService


@routes_api.route('/search/<index_name>', methods=['POST'])
@routes_api.route('/search/<index_name>/<start>/<hits_per_page>', methods=['POST'])
def search(index_name, start=0, hits_per_page=20, query='', region=None):
    try:
        search_service = Injector().get(SearchService)
        result = search_service.search_in_index(index_name, start, hits_per_page, query, region)
        response = {
            'total': result['hits']['total']['value'],
            'items': [item['_source'].to_dict() for item in result['hits']['hits']],
            'from': start,
            'size': hits_per_page
        }
        return response
    except Exception as ex:
        print(ex)
        return {
            'total': 0,
            'items': [],
            'from': start,
            'size': hits_per_page
        }