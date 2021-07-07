import json
from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from knox.models import AuthToken
from requests.exceptions import HTTPError
from rest_framework import status

from core.models import XDSConfiguration, XDSUIConfiguration, XDSUser

from .test_setup import TestSetUp


@tag('unit')
class ViewTests(TestSetUp):

    def test_xds_ui_config_view(self):
        """Test that making a GET request to the api gives us a JSON of the
            stored XDSUIConfiguration model"""
        url = reverse('xds_api:xds-ui-configuration')
        with patch('xds_api.views.XDSUIConfiguration.objects') as xds_ui_Obj:
            xds_config = XDSConfiguration(target_xis_metadata_api="test")
            xds_ui_cfg = XDSUIConfiguration(search_results_per_page=10,
                                            xds_configuration=xds_config)
            xds_ui_Obj.return_value = xds_ui_Obj
            xds_ui_Obj.first.return_value = xds_ui_cfg

            # create user, save user, login using client
            user = XDSUser.objects.create_user(self.email,
                                               self.password,
                                               first_name=self.first_name,
                                               last_name=self.last_name)
            _, token = AuthToken.objects.create(user)

            response = self.client \
                .get(url, HTTP_AUTHORIZATION='Token {}'.format(token))
            response_dict = json.loads(response.content)

            self.assertEqual(response_dict['search_results_per_page'],
                             xds_ui_cfg.search_results_per_page)
            self.assertEqual(response_dict['search_sort_options'], [])
            self.assertEqual(response_dict['course_highlights'], [])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_spotlight_courses(self):
        """test that calling the endpoint /api/spotlight-courses returns a
            list of documents for configured spotlight courses"""
        url = reverse('xds_api:spotlight-courses')

        with patch('xds_api.views.send_log_email'), \
                patch('xds_api.views.get_request') as get_request, \
                patch('xds_api.views.get_spotlight_courses_api_url') as \
                get_api_url:
            get_api_url.return_value = "www.test.com"
            http_resp = get_request.return_value
            get_request.return_value = http_resp
            http_resp.json.return_value = [{
                "test": "value"
            }]
            http_resp.status_code = 200

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_spotlight_courses_error(self):
        """test that calling the endpoint /api/spotlight-courses returns an
            http error if an exception a thrown while reaching out to XIS"""
        url = reverse('xds_api:spotlight-courses')
        errorMsg = "error reaching out to configured XIS API; " + \
                   "please check the XIS logs"

        with patch('xds_api.views.send_log_email'), \
                patch('xds_api.views.get_request') as get_request, \
                patch('xds_api.views.get_spotlight_courses_api_url') as \
                get_api_url:
            get_api_url.return_value = "www.test.com"
            get_request.side_effect = [HTTPError]

            response = self.client.get(url)
            responseDict = json.loads(response.content)

            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(responseDict['message'], errorMsg)

    def test_register_view(self):
        """Test that calling /api/auth/register creates a new user and
            returns the user along with a token"""
        url = reverse('xds_api:register')

        response = self.client.post(url, self.userDict)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(responseDict['token'] is not None)
        self.assertTrue(responseDict['user'] is not None)

    def test_login_view(self):
        """Test that calling /api/auth/login returns a token and user object
            if the credentials are valid"""
        url = reverse('xds_api:login')
        # create user, save user, login using client
        XDSUser.objects.create_user(self.email,
                                    self.password,
                                    first_name=self.first_name,
                                    last_name=self.last_name)

        response = self.client.post(url, self.userDict_login)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(responseDict['token'] is not None)
        self.assertTrue(responseDict['user'] is not None)

    def test_login_view_fail(self):
        """Test that calling /api/auth/login returns an error if the
            credentials are invalid"""
        url = reverse('xds_api:login')
        # create user, save user, login using client
        XDSUser.objects.create_user(self.email,
                                    self.password,
                                    first_name=self.first_name,
                                    last_name=self.last_name)

        response = self.client.post(url, self.userDict_login_fail)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_courses(self):
        """test that calling the endpoint /api/courses returns a single course
            for the given course ID"""
        doc_id = '123456'
        url = reverse('xds_api:get_courses', args=(doc_id,))

        with patch('xds_api.views.get_request') as get_request, \
                patch('xds_api.views.get_courses_api_url') as get_api_url:
            get_api_url.return_value = "www.test.com"
            http_resp = get_request.return_value
            get_request.return_value = http_resp
            http_resp.json.return_value = [{
                "test": "value"
            }]
            http_resp.status_code = 200

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_courses_error(self):
        """test that calling the endpoint /api/courses returns an
            http error if an exception a thrown while reaching out to XIS"""
        doc_id = '123456'
        url = reverse('xds_api:get_courses', args=(doc_id,))
        errorMsg = "error reaching out to configured XIS API; " + \
                   "please check the XIS logs"

        with patch('xds_api.views.get_request') as get_request, \
                patch('xds_api.views.get_courses_api_url') as get_api_url:
            get_api_url.return_value = "www.test.com"
            get_request.side_effect = [HTTPError]

            response = self.client.get(url)
            responseDict = json.loads(response.content)

            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(responseDict['message'], errorMsg)
