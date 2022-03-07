import logging

from django.contrib.auth.models import AnonymousUser
from elasticsearch_dsl import A, Search, connections

logger = logging.getLogger('dict_config_logger')


class BaseQueries():

    def __init__(self, host, index, user=AnonymousUser()):
        self.host = host
        self.index = index
        self.user = user
        self.search = Search(using='default', index=index)
        connections.create_connection(alias='default',
                                      hosts=[self.host, ], timeout=60)

    def filter_options(self):
        """Aggregates options for filter field in XSE"""

        # create filter aggregation and add it to search object
        filter_agg = A('terms', field='filter')
        self.search.aggs.bucket('filter_terms', filter_agg)
        setattr(self.search, 'size', 0)

        response = self.search.execute()

        return [option['key'] for option in
                response.aggs['filter_terms']['buckets']]
