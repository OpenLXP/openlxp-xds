import json
from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.test import APITestCase

from es_api import views


@tag('unit')
class ViewTests(APITestCase):

    def test_search_index_no_keyword(self):
        """Test that the /es-api/ endpoint sends an HTTP error when no
            keyword is provided"""
        url = reverse(views.search_index)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_index_with_keyword(self):
        """Test that the /es-api/ endpoint succeeds when a valid
            keyword is provided"""
        url = "%s?keyword=hello" % (reverse(views.search_index))
        with patch('es_api.views.search_by_keyword') as searchByKW, \
                patch('es_api.views.get_results') as getResults, \
                patch('es_api.views.SearchFilter.objects') as sfObj:
            sfObj.return_value = []
            sfObj.filter.return_value = []
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

    def test_gmlt(self):
        # Test that the /es-api/more-like-this/{doc_id} endpoint returns code
        # 200 when successful
        doc_id = 19
        url = reverse(views.get_more_like_this, args=(doc_id,))
        with patch('es_api.views.more_like_this') as moreLikeThis, \
                patch('es_api.views.get_results') as getResults:
            result_json = json.dumps({"test": "value"})
            moreLikeThis.return_value = {
                "hits": {
                    "total": {
                        "value": 1
                    }
                }
            }
            getResults.return_value = result_json
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gmlt_exception(self):
        # Test that the /es-api/more-like-this/{doc_id} endpoint returns a
        # server error when an exception is raised
        doc_id = 19
        errorMsg = "error executing ElasticSearch query; please check the logs"
        url = reverse(views.get_more_like_this, args=(doc_id,))
        with patch('es_api.views.more_like_this') as moreLikeThis:
            moreLikeThis.side_effect = [HTTPError]
            response = self.client.get(url)
            responseDict = json.loads(response.content)
            # print(responseDict)
            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(responseDict['message'], errorMsg)
