import json
import logging

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseServerError)
from requests.exceptions import HTTPError

from core.models import SearchFilter
from es_api.utils.queries import (get_results, more_like_this,
                                  search_by_keyword, spotlight_courses)

logger = logging.getLogger('dict_config_logger')


def search_index(request):
    """This method defines an API for sending keyword queries to ElasticSearch
        without using a model"""
    results = []
    keyword = ''
    filters = {
        'page': '1'
    }

    if request.GET.get('keyword'):
        keyword = request.GET['keyword']

    if (request.GET.get('p')) and (request.GET.get('p') != ''):
        filters['page'] = request.GET['p']

    if (request.GET.get('sort')) and (request.GET.get('sort') != ''):
        filters['sort'] = request.GET['sort']

    if keyword != '':
        errorMsg = {
            "message": "error executing ElasticSearch query; Please contact " +
                       "an administrator"
        }
        errorMsgJSON = json.dumps(errorMsg)

        try:
            search_filters = SearchFilter.objects.filter(active=True)

            # only add the filters that are defined in the configuration, the
            # rest is ignored
            for curr_filter in search_filters:
                if (request.GET.get(curr_filter.field_name)) \
                        and (request.GET.get(curr_filter.field_name) != ''):
                    filters[curr_filter.field_name] = \
                        request.GET.getlist(curr_filter.field_name)

            response = search_by_keyword(keyword=keyword, filters=filters)
            results = get_results(response)
        except HTTPError as http_err:
            logger.error(http_err)
            return HttpResponseServerError(errorMsgJSON,
                                           content_type="application/json")
        except Exception as err:
            logger.error(err)
            return HttpResponseServerError(errorMsgJSON,
                                           content_type="application/json")
        else:
            logger.info(results)
            return HttpResponse(results, content_type="application/json")
    else:
        error = {
            "message": "Request is missing 'keyword' query paramater"
        }
        errorJson = json.dumps(error)
        return HttpResponseBadRequest(errorJson,
                                      content_type="application/json")


def get_more_like_this(request, doc_id):
    """This method defines an API for fetching results using the
        more_like_this feature from elasticsearch. """
    results = []

    errorMsg = {
        "message": "error executing ElasticSearch query; " +
                   "please check the logs"
        }
    errorMsgJSON = json.dumps(errorMsg)

    try:
        response = more_like_this(doc_id=doc_id)
        results = get_results(response)
    except HTTPError as http_err:
        logger.error(http_err)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")
    except Exception as err:
        logger.error(err)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")
    else:
        logger.info(results)
        return HttpResponse(results, content_type="application/json")


def get_spotlight_courses(request):
    """This method defines an API for fetching configured course spotlights
        from elasticsearch. """
    results = []

    errorMsg = {
        "message": "error executing ElasticSearch query; " +
                   "please check the logs"
        }
    errorMsgJSON = json.dumps(errorMsg)

    try:
        results = spotlight_courses()
        resultJSON = json.dumps(results)
    except HTTPError as http_err:
        logger.error(http_err)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")
    except Exception as err:
        logger.error(err)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")
    else:
        logger.info(results)
        return HttpResponse(resultJSON, content_type="application/json")
