from injector import Module, Injector, singleton, provider
from helpers import ElasticStorage
from services import SearchService, FilterService, ImportService
from helpers import enabled_providers

class AppModule(Module):
    @singleton
    @provider
    def provide_storage(self) -> ElasticStorage:
        return ElasticStorage()

    @singleton
    @provider
    def provide_import_service(self) -> ImportService:
        return ImportService(self.provide_storage(), enable_providers=enabled_providers)

    @singleton
    @provider
    def provide_search_service(self):
        return SearchService(self.provide_storage())

    @singleton
    @provider
    def provide_filter_service(self):
        return FilterService(self.provide_storage())


injector = Injector(AppModule())
