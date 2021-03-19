import json
import logging
import os

from elasticsearch_dsl import Q, Search, connections
from elasticsearch_dsl.query import MoreLikeThis

from core.models import XDSConfiguration

connections.create_connection(alias='default',
                              hosts=[os.environ.get('ES_HOST'), ], timeout=60)

logger = logging.getLogger('dict_config_logger')


def get_page_start(page_number, page_size):
    """This helper method returns the starting index of a page given the page
         number, the size, and a start point of 0"""
    if (page_number <= 1):
        return 0
    else:
        start_index = (page_number - 1) * page_size

        return start_index

def get_page_start(page_number, page_size):
    """This helper method returns the starting index of a page given the page
         number, the size, and a start point of 0"""
    if (page_number <= 1):
        return 0
    else:
        start_index = (page_number - 1) * page_size

        return start_index


def search_by_keyword(keyword="", page="1"):
    """This method takes in a keyword string + a page number and queries
        ElasticSearch for the term then returns the Response Object"""
    q = Q("bool", should=[Q("match", Course__CourseDescription=keyword),
                          Q("match", Course__CourseTitle=keyword)],
          minimum_should_match=1)
    s = Search(using='default', index=os.environ.get('ES_INDEX')).query(q)
    configuration = XDSConfiguration.objects.first()
    page_size = configuration.search_results_per_page
    start_index = get_page_start(int(page), page_size)
    end_index = start_index + page_size
    s = s[start_index:end_index]
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
