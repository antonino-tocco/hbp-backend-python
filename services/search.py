from injector import inject
from helpers.storage import Storage

class SearchService:
    def __init__(self, storage: Storage):
        super(SearchService, self).__init__()
        self.__name__ = "search_service"
        self.storage = storage

    def search_in_index(self, index_name, query='', start=0, hits_per_page=20):
        try:
            return self.storage.search(index_name, start, hits_per_page)
        except Exception as ex:
            print(ex)
            raise ex
