import json
import logging

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseServerError)
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from configurations.models import CourseInformationMapping, XDSConfiguration
from core.models import SearchFilter
from es_api.utils.queries import XSEQueries

logger = logging.getLogger('dict_config_logger')

CONTACT_ADMIN = "Please contact an administrator"


class SearchIndexView(APIView):
    """This method defines an API for sending keyword queries to ElasticSearch
            without using a model"""

    def get_request_attributes(self, request):
        """helper method to get attributes"""
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

        return keyword, filters

    def get(self, request):
        results = []

        keyword, filters = self.get_request_attributes(request)

        if keyword != '':
            errorMsg = {
                "message": "error executing ElasticSearch query; " +
                CONTACT_ADMIN
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

                queries = XSEQueries(
                    XDSConfiguration.objects.first().target_xse_host,
                    XDSConfiguration.objects.first().target_xse_index,
                    user=request.user)
                response = queries.search_by_keyword(
                    keyword=keyword, filters=filters)
                results = queries.get_results(response)
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


class SearchDerivedView(APIView):
    """This method defines an API for querying to ElasticSearch
            for derived experiences"""

    def get_request_attributes(self, request):
        """helper method to get attributes"""
        reference = ''
        filters = {
            'page': '1'
        }

        if request.GET.get('reference'):
            reference = request.GET['reference']

        if (request.GET.get('p')) and (request.GET.get('p') != ''):
            filters['page'] = request.GET['p']

        return reference, filters

    def get(self, request):
        results = []

        reference, filters = self.get_request_attributes(request)

        if reference != '':
            errorMsg = {
                "message": "error executing ElasticSearch query; " +
                CONTACT_ADMIN
            }
            errorMsgJSON = json.dumps(errorMsg)

            try:
                queries = XSEQueries(
                    XDSConfiguration.objects.first().target_xse_host,
                    XDSConfiguration.objects.first().target_xse_index,
                    user=request.user)
                response = queries.search_for_derived(
                    reference=reference, filters=filters)
                results = queries.get_results(response)
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
                "message": "Request is missing 'reference' query " +
                "parameter"
            }
            errorJson = json.dumps(error)
            return HttpResponseBadRequest(errorJson,
                                          content_type="application/json")


class SearchCompetencyView(APIView):
    """This method defines an API for querying to ElasticSearch
            for competencies"""

    def get_request_attributes(self, request):
        """helper method to get attributes"""
        reference = ''
        filters = {
            'page': '1'
        }

        if request.GET.get('reference'):
            reference = request.GET['reference']

        if (request.GET.get('p')) and (request.GET.get('p') != ''):
            filters['page'] = request.GET['p']

        return reference, filters

    def get(self, request):
        results = []

        reference, filters = self.get_request_attributes(request)

        if reference != '':
            errorMsg = {
                "message": "error executing ElasticSearch query; " +
                CONTACT_ADMIN
            }
            errorMsgJSON = json.dumps(errorMsg)

            try:
                queries = XSEQueries(
                    XDSConfiguration.objects.first().target_xse_host,
                    XDSConfiguration.objects.first().target_xse_index,
                    user=request.user)
                response = queries.search_by_competency(
                    comp_uuid=reference, filters=filters)
                results = queries.get_results(response)
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
                "message": "Request is missing 'reference' query " +
                "parameter"
            }
            errorJson = json.dumps(error)
            return HttpResponseBadRequest(errorJson,
                                          content_type="application/json")


class GetMoreLikeThisView(APIView):
    """This method defines an API for fetching results using the
            more_like_this feature from elasticsearch for
            more like this courses section of UI. """

    def get(self, request, doc_id):
        results = []

        errorMsg = {
            "message": "error executing ElasticSearch query; " +
            "please check the logs"
        }
        errorMsgJSON = json.dumps(errorMsg)

        try:
            queries = XSEQueries(
                XDSConfiguration.objects.first().target_xse_host,
                XDSConfiguration.objects.first().target_xse_index,
                user=request.user)
            response = queries.more_like_this(doc_id=doc_id)
            results = queries.get_results(response)
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


class GetSimilarCoursesView(APIView):
    """This method defines an API for fetching results by sending key words
            to elasticsearch and looking for similar courses. """

    def get(self, request, key):
        results = []
        if key != '':
            errorMsg = {
                "message": "error executing ElasticSearch query; " +
                CONTACT_ADMIN
            }
            errorMsgJSON = json.dumps(errorMsg)

            try:
                queries = XSEQueries(
                    XDSConfiguration.objects.first().target_xse_host,
                    XDSConfiguration.objects.first().target_xse_index,
                    user=request.user)
                response = queries.similar_courses(
                    keyword=key)
                results = queries.get_results(response)
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
                "message": "Request is missing 'key' query parameter"
            }
            errorJson = json.dumps(error)
            return HttpResponseBadRequest(errorJson,
                                          content_type="application/json")


class FiltersView(APIView):
    """This method defines an API for performing a filter search"""

    def get(self, request):
        course_mapping = CourseInformationMapping.objects.first()

        results = []
        filters = {}
        page_num = 1

        if (request.GET.get('p')) and (request.GET.get('p') != ''):
            page_num = int(request.GET['p'])

        if (request.GET.get(course_mapping.course_title) and
                request.GET.get(course_mapping.course_title) != ''):
            filters[course_mapping.course_title] = \
                request.GET[course_mapping.course_title]

        if (request.GET.get(course_mapping.course_provider) and
                request.GET.get(course_mapping.course_provider) != ''):
            filters[course_mapping.course_provider] = \
                request.GET[course_mapping.course_provider]

        if (request.GET.get('CourseInstance.CourseLevel') and
                request.GET.get('CourseInstance.CourseLevel') != ''):
            filters['CourseInstance.CourseLevel'] = \
                request.GET['CourseInstance.CourseLevel']

        errorMsg = {
            "message": "error executing ElasticSearch query; " +
            CONTACT_ADMIN
        }
        errorMsgJSON = json.dumps(errorMsg)

        try:
            queries = XSEQueries(
                XDSConfiguration.objects.first().target_xse_host,
                XDSConfiguration.objects.first().target_xse_index,
                user=request.user)
            response = queries.search_by_filters(
                page_num=page_num, filters=filters)
            results = queries.get_results(response)
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


class SuggestionsView(APIView):
    """
    This method defines an API for retrieving suggested items from Elastic
    """

    def get(self, request):
        # if partial not passed in or empty, return failstate
        if ('partial' not in request.GET or request.GET['partial'] == ''):
            return Response({"message": "No partial data sent"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            queries = XSEQueries(
                XDSConfiguration.objects.first().target_xse_host,
                XDSConfiguration.objects.first().target_xse_index)
            response = queries.suggest(
                partial=request.GET['partial'])

            results = response.suggest.to_dict()['autocomplete_suggestion']

            return Response(results, status=status.HTTP_200_OK)
        except Exception as err:
            logger.error(err)
            return Response({"message": err.args[0]},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
