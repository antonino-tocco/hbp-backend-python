from injector import singleton
from services import SearchService
from helpers.storage import ElasticStorage

def configure(binder):
    binder.bind(SearchService, to=SearchService(ElasticStorage()), scope=singleton)