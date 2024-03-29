import math
from icecream import ic
from injector import inject, singleton
from helpers.storage import ElasticStorage


class SearchService:
    @inject
    def __init__(self, storage: ElasticStorage):
        super(SearchService, self).__init__()
        self.__name__ = "search_service"
        self.storage = storage

    def get_all_in_index(self, index_name, data_type=None, query='', secondary_region=None, cell_type=None, species=None, ids=[]) -> []:
        try:
            num_page = 0
            hits_per_page = 100
            total_pages = 1
            fetched = False
            all_items = []
            while num_page < (total_pages - 1) or fetched is False:
                start = num_page * hits_per_page
                results = self.storage.search(index_name, start, hits_per_page, data_type, query, secondary_region, cell_type, species, ids=ids)
                total_items = results['hits']['total']['value']
                total_pages = math.ceil(total_items / hits_per_page)
                items = [item['_source'].to_dict() for item in results['hits']['hits']]
                all_items.extend(items)
                num_page = num_page + 1
                fetched = True
            return all_items
        except Exception as ex:
            ic(ex)
            raise ex

    def search_connections(self, start=0, hits_per_page=20, query='', presynaptic=None, postsynaptic=None):
        try:
            return self.storage.search_connections(start, hits_per_page, query, presynaptic, postsynaptic)
        except Exception as ex:
            ic(ex)
            raise ex

    def search_in_index(self, index_name, start=0, hits_per_page=20, data_type=None, query='', secondary_region=None, cell_type=None, species=None, layers=None, channels=None, receptors=None, implementers=None, model_concepts=None, ids=[]) -> []:
        try:
            return self.storage.search(index_name, start, hits_per_page, data_type, query, secondary_region, cell_type, species, layers=layers, channels=channels, receptors=receptors, implementers=implementers, model_concepts=model_concepts, ids=ids)
        except Exception as ex:
            ic(ex)
            raise ex
