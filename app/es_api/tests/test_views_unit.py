import json
from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.test import APITestCase

from django.test import override_settings


@tag('unit')
class ViewTests(APITestCase):

    def setUp(self):
        settings_manager = override_settings(SECURE_SSL_REDIRECT=False)
        settings_manager.enable()
        self.addCleanup(settings_manager.disable)

    def test_search_index_no_keyword(self):
        """
        Test that the /es-api/ endpoint sends an HTTP error when no
        keyword is provided
        """
        url = reverse('es_api:search-index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_index_with_keyword(self):
        """
        Test that the /es-api/ endpoint succeeds when a valid
        keyword is provided
        """
        url = "%s?keyword=hello&p=1&sort=1" % (reverse('es_api:search-index'))
        with patch('es_api.views.XSEQueries') as query, \
                patch('es_api.views.SearchFilter.objects') as sfObj, \
                patch('es_api.views.XDSConfiguration.objects'):
            sfObj.return_value = []
            sfObj.filter.return_value = []
            result_json = json.dumps({"test": "value"})
            query.get_results.return_value = result_json
            query.return_value = query
            response = self.client.get(url)
            # print(response.content)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(json.loads(response.content), {'test': "value"})

    def test_gmlt(self):
        """
        Test that the /es-api/more-like-this/{doc_id} endpoint returns code
        200 when successful
        """
        doc_id = 19
        url = reverse('es_api:get-more-like-this', args=(doc_id,))
        with patch('es_api.views.XSEQueries') as query, \
                patch('es_api.views.XDSConfiguration.objects'):
            result_json = json.dumps({"test": "value"})
            query.get_results.return_value = result_json
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gmlt_exception(self):
        """
        Test that the /es-api/more-like-this/{doc_id} endpoint returns a
        server error when an exception is raised
        """
        doc_id = 19
        errorMsg = "error executing ElasticSearch query; please check the logs"
        url = reverse('es_api:get-more-like-this', args=(doc_id,))
        with patch('es_api.views.XSEQueries.more_like_this') as query, \
                patch('es_api.views.XDSConfiguration.objects'):
            query.more_like_this.side_effect = [HTTPError]
            response = self.client.get(url)
            responseDict = json.loads(response.content)
            # print(responseDict)
            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(responseDict['message'], errorMsg)

    def test_similar_courses(self):
        """
        Test that the /es-api/similar-courses/{key} endpoint returns code
        200 when successful
        """
        key = 'test'
        url = reverse('es_api:get-similar-courses', args=(key,))
        with patch('es_api.views.XSEQueries') as query, \
                patch('es_api.views.XDSConfiguration.objects'):
            result_json = json.dumps({"test": "value"})
            query.get_results.return_value = result_json
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filters(self):
        """
        Test that the /es-api/filter-search? endpoint returns code
        200 when successful
        """
        with patch('es_api.utils.queries.'
                   'CourseInformationMapping.objects') as course_mapping:
            course_mapping.course_title = "Course.CourseTitle"
            course_mapping.course_provider = "Course.CourseProviderName"

            url = "%s?Course.CourseTitle=hi" % (reverse('es_api:filters')) + \
                  "&Course.CourseProviderName=" \
                  "test&CourseInstance.CourseLevel=3&p=1"
            with patch('es_api.views.XSEQueries') as query, \
                    patch('es_api.views.XDSConfiguration.objects'):
                result_json = json.dumps({"test": "value"})
                query.get_results.return_value = result_json
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filters_exception(self):
        """
        Test that the /es-api/filter-search? endpoint returns a server error
        when an exception is raised
        """
        with patch('es_api.utils.queries.'
                   'CourseInformationMapping.objects'):
            errorMsg = "error executing ElasticSearch query; " \
                       "Please contact " + \
                       "an administrator"
            url = "%s?Course.CourseTitle=hi" % (reverse('es_api:filters'))
            with patch('es_api.views.XSEQueries.search_by_filters') \
                    as searchByFilters:
                searchByFilters.side_effect = [HTTPError]
                response = self.client.get(url)
                responseDict = json.loads(response.content)
                self.assertEqual(response.status_code,
                                 status.HTTP_500_INTERNAL_SERVER_ERROR)
                self.assertEqual(responseDict['message'], errorMsg)

    def test_suggestions(self):
        """
        Test that the /es-api/suggest? endpoint returns code
        200 when successful
        """
        url = "%s?partial=hi" % (reverse('es_api:suggest'))
        with patch('es_api.views.XSEQueries') as query, \
                patch('es_api.views.XDSConfiguration.objects'):
            result_json = {"autocomplete_suggestion": "test"}
            query.to_dict.return_value = result_json
            query.suggest = query
            query.suggest.return_value = query

            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.content, b'"test"')

    def test_suggestions_exception(self):
        """
        Test that the /es-api/suggest? endpoint returns a server error
        when an exception is raised
        """
        url = "%s?partial=hi" % (reverse('es_api:suggest'))

        response = self.client.get(url)

        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_suggestions_missing(self):
        """
        Test that the /es-api/suggest? endpoint returns a bad request
        when an missing partial info
        """
        url = "%s?partial=" % (reverse('es_api:suggest'))

        response = self.client.get(url)

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)


@tag('unit')
class SearchDerivedTests(APITestCase):

    def setUp(self):
        settings_manager = override_settings(SECURE_SSL_REDIRECT=False)
        settings_manager.enable()
        self.addCleanup(settings_manager.disable)

    def test_search_derived_no_reference(self):
        """
        Test that the /es-api/ endpoint sends an HTTP error when no
        reference is provided
        """
        url = reverse('es_api:search-derived')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_derived_with_reference(self):
        """
        Test that the /es-api/ endpoint succeeds when a valid
        reference is provided
        """
        url = "%s?reference=hello&p=1" % (reverse('es_api:search-derived'))
        with patch('es_api.views.XSEQueries') as query, \
                patch('es_api.views.SearchFilter.objects') as sf1Obj, \
                patch('es_api.views.XDSConfiguration.objects'):
            sf1Obj.return_value = []
            sf1Obj.filter.return_value = []
            result_json = json.dumps({"test": "value"})
            query.get_results.return_value = result_json
            query.return_value = query
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(json.loads(response.content), {'test': "value"})


@tag('unit')
class SearchCompetencyTests(APITestCase):

    def setUp(self):
        settings_manager = override_settings(SECURE_SSL_REDIRECT=False)
        settings_manager.enable()
        self.addCleanup(settings_manager.disable)

    def test_search_competency_no_reference(self):
        """
        Test that the /es-api/ endpoint sends an HTTP error when no
        reference is provided
        """
        url = reverse('es_api:search-competency')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_derived_with_reference(self):
        """
        Test that the /es-api/ endpoint succeeds when a valid
        reference is provided
        """
        url = "%s?reference=hello&p=1" % (reverse('es_api:search-competency'))
        with patch('es_api.views.XSEQueries') as query, \
                patch('es_api.views.SearchFilter.objects') as sf1Obj, \
                patch('es_api.views.XDSConfiguration.objects'):
            sf1Obj.return_value = []
            sf1Obj.filter.return_value = []
            result_json = json.dumps({"test": "value"})
            query.get_results.return_value = result_json
            query.return_value = query
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(json.loads(response.content), {'test': "value"})
