import os
from functools import reduce
from injector import singleton
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, Q
from . import Storage


class ElasticStorage(Storage):
    def __init__(self, host=os.getenv('ELASTIC_SEARCH_URL')):
        assert(host is not None)
        super(ElasticStorage, self).__init__()
        self.es = Elasticsearch(hosts=[host])

    def store_object(self, index, identifier, obj):
        try:
            self.es.index(index, id=identifier, body=obj)
        except Exception as ex:
            print(f"Exception storing object {ex}")
            
    def get_object(self, index, identifier):
        try:
            return self.es.get(index, id=identifier)
        except Exception as ex:
            print(ex)

    def get_terms_aggregation(self, fields=[]):
        response = {}
        try:
            for (key, value) in fields:
                es_search = Search(using=self.es)
                es_search.aggs.bucket(key, A('terms', field=f'{key}.{value}'))
                results = es_search.execute()
                values = [item['key'] for item in results.aggregations[key].buckets]
                response[key] = values
        except Exception as ex:
            print(ex)
        return response

    def search(self, index, start=0, hits_per_page=20, data_type=None, query='', ids=[], secondary_region=None, cell_type=None, species=None, sort_fields=['name']):
        try:
            s = Search(using=self.es)
            s = s.index(index)
            if ids is not None and len(ids) > 0:
                s = s.query('ids', values=ids)
            else:
                s = s[start:start + hits_per_page]
                if data_type is not None:
                    s = s.filter('term', **{'type.keyword': data_type})
                if secondary_region is not None and secondary_region != '':
                    s = s.filter('term', **{'secondary_region.keyword': secondary_region})
                if cell_type is not None and cell_type != '':
                    s = s.filter('term', **{'cell_type.keyword': cell_type})
                if species is not None and species != '':
                    s = s.filter('term', **{'species.keyword': species})
                if query is not None and query != '':
                    s = s.query('multi_match', query=query, fields=['name', 'description'])
                if sort_fields:
                    s = s.sort(item for item in sort_fields)
            return s.execute()
        except Exception as ex:
            raise ex