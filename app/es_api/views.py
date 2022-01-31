import json
import logging

from core.models import SearchFilter
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseServerError)
from es_api.utils.queries import (get_results, more_like_this,
                                  search_by_filters, search_by_keyword)
from requests.exceptions import HTTPError
from rest_framework.views import APIView

logger = logging.getLogger('dict_config_logger')


class SearchIndexView(APIView):
    """This method defines an API for sending keyword queries to ElasticSearch
            without using a model"""

    def get(self, request):
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
                "message": "error executing ElasticSearch query; " +
                "Please contact an administrator"
            }
            errorMsgJSON = json.dumps(errorMsg)

            try:
                search_filters = SearchFilter.objects.filter(active=True)

                # only add the filters that are defined in the configuration,
                # the rest is ignored
                for curr_filter in search_filters:
                    if (request.GET.get(curr_filter.field_name)) and \
                            (request.GET.get(curr_filter.field_name) != ''):
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


class GetMoreLikeThisView(APIView):
    """This method defines an API for fetching results using the
            more_like_this feature from elasticsearch. """

    def get(self, request, doc_id):
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


class FiltersView(APIView):
    """This method defines an API for performing a filter search"""

    def get(self, request):
        results = []
        filters = {}
        page_num = 1

        if (request.GET.get('p')) and (request.GET.get('p') != ''):
            page_num = int(request.GET['p'])

        if (request.GET.get('Course.CourseTitle') and
                request.GET.get('Course.CourseTitle') != ''):
            filters['Course.CourseTitle'] = request.GET['Course.CourseTitle']

        if (request.GET.get('Course.CourseProviderName') and
                request.GET.get('Course.CourseProviderName') != ''):
            filters['Course.CourseProviderName'] = \
                request.GET['Course.CourseProviderName']

        if (request.GET.get('CourseInstance.CourseLevel') and
                request.GET.get('CourseInstance.CourseLevel') != ''):
            filters['CourseInstance.CourseLevel'] = \
                request.GET['CourseInstance.CourseLevel']

        errorMsg = {
            "message": "error executing ElasticSearch query; Please contact " +
            "an administrator"
        }
        errorMsgJSON = json.dumps(errorMsg)

        try:
            response = search_by_filters(page_num, filters)
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
