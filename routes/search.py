from . import routes_api
from services import search

@routes_api.route('/search/<index_name>', method=['GET'])
@routes_api.route('/search/<index_name>/<start>/<hits_per_page>', method=['GET'])
def search(index_name, start=0, hits_per_page=20):
    results = search(index_name, start, hits_per_page)
    return results