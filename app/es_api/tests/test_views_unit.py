from unittest.mock import patch
from rest_framework.test import APITestCase
from django.test import tag
from django.urls import reverse
from rest_framework import status
from es_api import views
import json


@tag('unit')
class ViewTests(APITestCase):

    def test_search_index_no_keyword(self):
        """Test that the /es_api/ endpoint sends an HTTP error when no
            keyword is provided"""
        url = reverse(views.search_index)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_index_with_keyword(self):
        """Test that the /es_api/ endpoint succeeds when a valid
            keyword is provided"""
        url = "%s?keyword=hello" % (reverse(views.search_index))
        with patch('es_api.views.search_by_keyword') as searchByKW, \
            patch('es_api.views.get_results') as getResults:
            result_json = json.dumps({"test": "value"})
            searchByKW.return_value = {
                "hits": {
                    "total": {
                        "value": 1
                    }
                }
            }
            getResults.return_value = result_json
            response = self.client.get(url)
            # print(response.content)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(json.loads(response.content), {'test': "value"})
