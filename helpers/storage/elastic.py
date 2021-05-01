import os
from functools import reduce
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
            for (key, item) in fields:
                es_search = Search(using=self.es)
                es_search = es_search.index(index_name)
                if data_type is not None:
                    es_search = es_search.filter('term', **{'type.keyword': data_type})

                if item is not None:
                    es_search.aggs.bucket(key, A('terms', field=f'{key}.{item}'))
                else:
                    es_search.aggs.bucket(key, A('terms', field=f'{key}'))
                results = es_search.execute()
                values = [item['key'] for item in results.aggregations[key].buckets]
                response[key] = values
        except Exception as ex:
            print(ex)
        return response

    def search_connections(self, start=0, hits_per_page=20, query='', presynaptic=None, postsynaptic=None):
        try:
            s = Search(using=self.es)
            s = s.index('dataset')
            s = s.filter('term', **{'type.keyword': 'connection'})
            s = s[start: start + hits_per_page]
            if query is not None and query != '':
                s = s.query('multi_match', query=query, fields=['presynaptic.name', 'presynaptic.description',
                                                                'postsynaptic.name', 'postsynaptic.description'])
            if presynaptic:
                for key in presynaptic:
                    values = presynaptic[key]
                    if isinstance(values, str):
                        if values != '':
                            s = s.filter('term', **{f'presynaptic.{key}.keyword': values})
                    elif values:
                        if len(values) > 0:
                            s = s.filter('terms', **{f'presynaptic.{key}.keyword': values})

            if postsynaptic:
                for key in postsynaptic:
                    values = postsynaptic[key]
                    if isinstance(values, str):
                        if values != '':
                            s = s.filter('term', **{f'postsynaptic.{key}.keyword': values})
                    elif values:
                        if len(values) > 0:
                            s = s.filter('terms', **{f'postsynaptic.{key}.keyword': values})
            return s.execute()
        except Exception as ex:
            raise ex

    def search(self, index, start=0, hits_per_page=20, data_type=None, query='', secondary_region=None,
               cell_type=None, species=None, layers=None, channels=None, receptors=None,
               implementers=None, model_concepts=None, ids=None, sort_fields=['name.keyword']):
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
                        if len(secondary_region) > 0:
                            s = s.filter('terms', **{'secondary_region.keyword': secondary_region})
                if cell_type is not None:
                    if isinstance(cell_type, str):
                        if cell_type != '':
                            s = s.filter('term', **{'cell_type.keyword': cell_type})
                    elif cell_type:
                        if len(cell_type) > 0:
                            s = s.filter('terms', **{'cell_type.keyword': cell_type})
                if species is not None:
                    if isinstance(species, str):
                        if species != '':
                            s = s.filter('term', **{'species.keyword': species})
                    elif species:
                        if len(species) > 0:
                            s = s.filter('terms', **{'species.keyword': species})
                if channels is not None:
                    if isinstance(channels, str):
                        if channels != '':
                            s = s.filter('term', **{'channels.keyword': channels})
                    elif channels:
                        if len(channels) > 0:
                            s = s.filter('terms', **{'channels.keyword': channels})
                if layers is not None:
                    if isinstance(layers, str):
                        if layers != '':
                            s = s.filter('term', **{'layers.keyword': layers})
                    elif layers:
                        if len(layers) > 0:
                            s = s.filter('terms', **{'layers.keyword': layers})
                if receptors is not None:
                    if isinstance(receptors, str):
                        if receptors != '':
                            s = s.filter('term', **{'receptors.keyword': receptors})
                    elif receptors:
                        if len(receptors) > 0:
                            s = s.query('terms', **{'receptors.keyword': receptors})
                if model_concepts is not None:
                    if isinstance(model_concepts, str):
                        if model_concepts != '':
                            s = s.filter('term', **{'model_concepts.keyword': model_concepts})
                    elif model_concepts:
                        if len(model_concepts) > 0:
                            s = s.query('terms', **{'model_concepts.keyword': model_concepts})
                if implementers is not None:
                    if isinstance(implementers, str):
                        if implementers != '':
                            s = s.filter('term', **{'implementers.keyword': implementers})
                    elif implementers:
                        if len(implementers) > 0:
                            s = s.query('terms', **{'implementers.keyword': implementers})
                if query is not None and query != '':
                    splitted_query = list(map(lambda x: x.strip(' \n\t'), query.split('|')))
                    wildcard_queries = [f"*{query}*" for query in splitted_query]
                    all_queries = [Q('query_string',  **{'name.keyword': wildcard_query}) |\
                        Q('query_string',  **{'description.keyword': wildcard_query}) |\
                        Q('query_string', **{'cell_type.keyword': wildcard_query}) |\
                        Q('query_string', **{'species.keyword': wildcard_query}) |\
                        Q('query_string', **{'channels.keyword': wildcard_query}) |\
                        Q('query_string', **{'model_concepts.keyword': wildcard_query}) |\
                        Q('query_string', **{'model_types.keyword': wildcard_query}) |\
                        Q('query_string', **{'layers.keyword': wildcard_query}) for wildcard_query in wildcard_queries]
                    queries = Q('bool', should=all_queries, minimum_should_match=1)
                    s = s.query(queries)
                if sort_fields:
                    s = s.sort(*sort_fields)
            results = s.execute()
            return results
        except Exception as ex:
            raise ex