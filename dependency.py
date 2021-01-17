from injector import Module, Injector, singleton, provider
from helpers import ElasticStorage
from services import SearchService, FilterService, ImportService, DownloadService
from helpers import enabled_dataset_providers, enabled_model_providers

class AppModule(Module):
    @singleton
    @provider
    def provide_storage(self) -> ElasticStorage:
        return ElasticStorage()

    @singleton
    @provider
    def provide_import_service(self) -> ImportService:
        return ImportService(self.provide_storage(), enabled_dataset_providers=enabled_dataset_providers, enabled_model_providers=enabled_model_providers)

    @singleton
    @provider
    def provide_search_service(self) -> SearchService:
        return SearchService(storage=self.provide_storage())

    @singleton
    @provider
    def provide_filter_service(self) -> FilterService:
        return FilterService(self.provide_storage())

    @singleton
    @provider
    def provide_download_service(self) -> DownloadService:
        return DownloadService()


injector = Injector(AppModule)
