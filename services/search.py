from injector import  inject, singleton
from helpers.storage import ElasticStorage


class SearchService:
    @inject
    def __init__(self, storage: ElasticStorage):
        super(SearchService, self).__init__()
        self.__name__ = "search_service"
        self.storage = storage


    def search_in_index(self, index_name, start=0, hits_per_page=20,  query='', secondary_region=None) -> []:
        try:
            return self.storage.search(index_name, start, hits_per_page, query, secondary_region)
        except Exception as ex:
            print(ex)
            raise ex
