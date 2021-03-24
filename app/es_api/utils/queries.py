import json
import logging
import os

from elasticsearch_dsl import Q, Search, connections, A
from elasticsearch_dsl.query import MoreLikeThis

from core.models import XDSConfiguration, XDSUIConfiguration, SearchFilter
from es_api.searches import MetadataSearch

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


def add_search_aggregations(filter_set, search):
    """This helper method takes in a search object and a queryset of filters
        then creates an aggregation for each filter"""
    for curr_filter in filter_set:

        # this is needed because elastic search only filters on keyword fields
        full_field_name = curr_filter.field_name + '.keyword'
        curr_agg = A(curr_filter.filter_type, field=full_field_name)
        search.aggs.bucket(curr_filter.display_name, curr_agg)
    
    return

def add_search_filters(search, filters):
    """This helper method iterates through the filters and adds them
        to the search query"""
    result_search = search

    for filter_name in filters:
        if filter_name != 'page':
            logger.info(filter_name)
            logger.info(filters[filter_name])
            field_name = filter_name + '.keyword'
            result_search = result_search.post_filter('terms', \
                **{field_name: filters[filter_name]})
    
    return result_search


def search_by_keyword(keyword="", filters={}):
    """This method takes in a keyword string + a page number and queries
        ElasticSearch for the term then returns the Response Object"""
    q = Q("bool", should=[Q("match", Course__CourseDescription=keyword),
                          Q("match", Course__CourseTitle=keyword)],
          minimum_should_match=1)


    # setting up the search object 
    s = Search(using='default', index=os.environ.get('ES_INDEX')).query(q)

    # getting the page size for result pagination
    configuration = XDSConfiguration.objects.first()
    uiConfig = configuration.xdsuiconfiguration
    search_filters = SearchFilter.objects.filter(xds_ui_configuration=uiConfig)

    # create aggregations for each filter
    add_search_aggregations(filter_set=search_filters, search=s)

    # add filters to the search query
    s = add_search_filters(search=s, filters=filters)
    
    page_size = uiConfig.search_results_per_page
    start_index = get_page_start(int(filters['page']), page_size)
    end_index = start_index + page_size
    s = s[start_index:end_index]

    # call to elasticsearch to execute the query
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
    agg_dict = response.aggregations.to_dict()

    for hit in response:
        hit_dict = hit.to_dict()

        # adding the meta data to the dictionary
        hit_dict['meta'] = hit.meta.to_dict()
        hit_arr.append(hit_dict)

    for key in agg_dict:
        search_filter = SearchFilter.objects.filter(display_name=key).first()
        filter_obj = agg_dict[key]
        filter_obj['field_name'] = search_filter.field_name

    resultObj = {
        "hits": hit_arr,
        "total": response.hits.total.value,
        "aggregations": agg_dict
    }

    return json.dumps(resultObj)
