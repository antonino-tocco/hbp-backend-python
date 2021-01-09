from injector import Module, Injector, singleton, provider
from helpers import Storage, ElasticStorage
from services import SearchService, FilterService

class AppModule(Module):
    @singleton
    @provider
    def provide_storage(self) -> ElasticStorage:
        return ElasticStorage()
    def provide_search_service(self):
        return SearchService(self.provide_storage())
    def provide_filter_service(self):
        return FilterService(self.provide_storage())

injector = Injector(AppModule())