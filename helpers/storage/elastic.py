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

    def get_terms_aggregation(self, index_name, data_type=None, fields=[]):
        response = {}
        try:
            for (key, value) in fields:
                es_search = Search(using=self.es)
                es_search = es_search.index(index_name)
                if data_type is not None:
                    es_search = es_search.filter('term', **{'type.keyword': data_type})
                es_search.aggs.bucket(key, A('terms', field=f'{key}.{value}'))
                results = es_search.execute()
                values = [item['key'] for item in results.aggregations[key].buckets]
                response[key] = values
        except Exception as ex:
            print(ex)
        return response

    def search(self, index, start=0, hits_per_page=20, data_type=None, query='', ids=None, secondary_region=None, cell_type=None, species=None, sort_fields=['name.keyword'], channels=None, receptors=None):
        try:
            s = Search(using=self.es)
            s = s.index(index)
            if ids:
                s = s.query('ids', values=ids)
            else:
                s = s[start:start + hits_per_page]
                if data_type is not None:
                    s = s.filter('term', **{'type.keyword': data_type})
                if secondary_region is not None:
                    if isinstance(secondary_region, str):
                        if secondary_region != '':
                            s = s.filter('term', **{'secondary_region.keyword': secondary_region})
                    elif secondary_region:
                        s = s.filter('terms', **{'secondary_region.keyword': secondary_region})
                if cell_type is not None:
                    if isinstance(cell_type, str):
                        if cell_type != '':
                            s = s.filter('term', **{'cell_type.keyword': cell_type})
                    elif cell_type:
                        s = s.filter('terms', **{'cell_type.keyword': cell_type})
                if species is not None:
                    if isinstance(species, str):
                        if species != '':
                            s = s.filter('term', **{'species.keyword': species})
                    elif species:
                        s = s.filter('terms', **{'species.keyword': species})
                if channels is not None:
                    if isinstance(channels, str):
                        if channels != '':
                            s = s.filter('term', **{'channels.keyword': channels})
                    elif channels:
                        s = s.filter('terms', **{'channels.keyword': channels})
                if receptors is not None:
                    if isinstance(receptors, str):
                        if receptors != '':
                            s = s.filter('term', **{'receptors.keyword': receptors})
                    elif receptors:
                        s = s.query('terms', **{'receptors.keyword': receptors})
                if query is not None and query != '':
                    s = s.query('multi_match', query=query, fields=['name', 'description'])
                if sort_fields:
                    s = s.sort(*sort_fields)
            return s.execute()
        except Exception as ex:
            raise ex