import math
from injector import  inject, singleton
from helpers.storage import ElasticStorage


class SearchService:
    @inject
    def __init__(self, storage: ElasticStorage):
        super(SearchService, self).__init__()
        self.__name__ = "search_service"
        self.storage = storage

    def get_all_in_index(self, index_name, query='', ids=[], secondary_region=None, cell_type=None, species=None) -> []:
        try:
            num_page = 0
            hits_per_page = 100
            total_pages = 1
            fetched = False
            all_items = []
            while num_page < (total_pages - 1) and fetched is False:
                start = num_page * hits_per_page
                results = self.storage.search(index_name, start, hits_per_page, query, ids, secondary_region, cell_type, species)
                total_items = results['hits']['total']['value']
                total_pages = math.ceil(total_items / hits_per_page)
                items = [item['_source'].to_dict() for item in results['hits']['hits']]
                all_items.extend(items)
                num_page = num_page + 1
                fetched = True
            return all_items
        except Exception as ex:
            print(ex)
            raise ex

    def search_in_index(self, index_name, start=0, hits_per_page=20,  query='', ids=[], secondary_region=None, cell_type=None, species=None) -> []:
        try:
            return self.storage.search(index_name, start, hits_per_page, query, ids, secondary_region, cell_type, species)
        except Exception as ex:
            print(ex)
            raise ex
