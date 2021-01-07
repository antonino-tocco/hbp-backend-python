from . import Storage
from elasticsearch import Elasticsearch

class ElasticStorage(Storage):

    def __init__(self, host=None):
        assert(host is not None)
        super(ElasticStorage, self).__init__(self)
        self.es = Elasticsearch(hosts=[host])

    def store_object(self, index, identifier, obj):
        try:
            self.es.index(index, id=identifier, body=obj)
        except Exception as ex:
            print(ex)
            
    def get_object(self, index, identifier):
        try:
            return self.es.get(index, id=identifier)
        except Exception as ex:
            print(ex)

    def search(self, index, query='', hits_per_page=20):
        try:
            return self.es.search(index=index)
        except Exception as ex:
            raise ex