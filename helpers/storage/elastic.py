import os
from injector import singleton
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A
from . import Storage


class ElasticStorage(Storage):
    def __init__(self, host=os.getenv('ELASTIC_SEARCH_URL')):
        assert(host is not None)
        super(ElasticStorage, self).__init__()
        self.es = Elasticsearch(hosts=[host])
        self.es_search = Search(using=self.es)

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

    def get_terms_aggregation(self, fields=[]):
        response = {}
        for (key, value) in fields:
            self.es_search.aggs.bucket(key, A('terms', field=f'{key}.{value}'))
            results = self.es_search.execute()
            values = [item['key'] for item in results.aggregations[key].buckets]
            response[key] = values
        return response

    def search(self, index, start=0, hits_per_page=20, query='', secondary_region=None):
        try:
            s = self.es_search
            s = s.index(index)
            s = s[start:start + hits_per_page]
            if secondary_region is not None and secondary_region != '':
                s = s.filter('term', **{'secondary_region.keyword': secondary_region})
            if query is not None and query != '':
                s = s.query('multi_match', query=query, fields=['name', 'description'])
            #self.es_search(index=index, from_=start, size=hits_per_page)
            return s.execute()
        except Exception as ex:
            raise ex