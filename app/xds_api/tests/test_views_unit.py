import json
from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import XDSConfiguration, XDSUIConfiguration


@tag('unit')
class ViewTests(APITestCase):

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

            response = self.client.get(url)
            response_dict = json.loads(response.content)
            print(response.content)

            self.assertEqual(response_dict['search_results_per_page'],
                             xds_ui_cfg.search_results_per_page)
            self.assertEqual(response_dict['search_sort_options'], [])
            self.assertEqual(response_dict['course_highlights'], [])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_spotlight_courses(self):
        """test that calling the endpoint /api/spotlight-courses returns a
            list of documents for configured spotlight courses"""
        url = reverse('xds_api:spotlight-courses')

        with patch('xds_api.views.get_request') as get_request, \
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
        """test that calling the endpoint /es-api/spotlight-courses returns an
            http error if an exception a thrown while reaching out to XIS"""
        url = reverse('xds_api:spotlight-courses')
        errorMsg = "error reaching out to configured XIS API; " + \
                   "please check the XIS logs"

        with patch('xds_api.views.get_request') as get_request, \
            patch('xds_api.views.get_spotlight_courses_api_url') as \
                get_api_url:
            get_api_url.return_value = "www.test.com"
            get_request.side_effect = [HTTPError]

            response = self.client.get(url)
            responseDict = json.loads(response.content)

            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(responseDict['message'], errorMsg)
