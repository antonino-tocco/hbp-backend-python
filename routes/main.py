from . import routes_api


@routes_api.route('/')
def home():
    return 'Server up!'
