import json
import logging
import os

from elasticsearch_dsl import Q, Search, connections
from elasticsearch_dsl.query import MoreLikeThis

connections.create_connection(alias='default',
                              hosts=[os.environ.get('ES_HOST'), ], timeout=60)

logger = logging.getLogger('dict_config_logger')


def search_by_keyword(keyword=""):
    """This method takes in a keyword string and queries ElasticSearch for the
        term then returns the Response Object"""
    q = Q("bool", should=[Q("match", Course__CourseDescription=keyword),
                          Q("match", Course__CourseTitle=keyword)],
          minimum_should_match=1)
    s = Search(using='default', index=os.environ.get('ES_INDEX')).query(q)
    response = s.execute()
    logger.info(response)

    return response


def more_like_this(doc_id):
    """This method takes in a doc ID and queries the elasticsearch index for
        courses with similar title or description"""
    likeObj = [
        {
            "_index": os.environ.get('ES_INDEX'),
            "_id": doc_id
        }
    ]
    s = Search(using='default', index=os.environ.get('ES_INDEX'))
    # We're going to match based only on two fields
    s = s.query(MoreLikeThis(like=likeObj, fields=['Course.CourseTitle',
                                                   'Course.CourseDescription'])
                )
    # only fetch the first 6 results
    # TODO: make the size configurable
    s = s[0:6]
    response = s.execute()
    logger.info(response)

    return response


def get_results(response):
    """This helper method consumes the response of an ElasticSearch Query and
        adds the hits to an array then returns a dictionary representing the
        results"""
    hit_arr = []

    for hit in response:
        hit_dict = hit.to_dict()
        # adding the meta data to the dictionary
        hit_dict['meta'] = hit.meta.to_dict()
        hit_arr.append(hit_dict)

    resultObj = {
        "hits": hit_arr,
        "total": response.hits.total.value
    }

    return json.dumps(resultObj)
