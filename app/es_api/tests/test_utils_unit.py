import json
from unittest.mock import patch

from django.test import SimpleTestCase, tag

from core.models import XDSConfiguration
from es_api.utils.queries import (get_page_start, get_results, more_like_this,
                                  search_by_keyword)


@tag('unit')
class UtilTests(SimpleTestCase):

    def test_get_results(self):
        """Test that calling get results on a Response Object returns a \
            dictionary with hits and a total"""
        with patch('elasticsearch_dsl.response') as response_obj:
            response_obj.return_value = {
                "hits": {
                    "total": {
                        "value": 1
                    }
                }
            }
            response_obj.hits.total.value = 1
            with patch('elasticsearch_dsl.response.hit.to_dict') as to_dict:
                to_dict.return_value = {
                    "key": "value"
                }
                result_json = get_results(response_obj)
                result_dict = json.loads(result_json)
                self.assertEqual(result_dict.get("total"), 1)
                self.assertEqual(len(result_dict.get("hits")), 0)

    def test_more_like_this(self):
        """"Test that calling more_like_this returns whatever response elastic
              search returns"""
        with patch('elasticsearch_dsl.Search.execute') as es_execute:
            resultVal = {
                "test": "test"
            }
            es_execute.return_value = {
                "test": "test"
            }
            result = more_like_this(1)
            self.assertEqual(result, resultVal)

    def test_search_by_keyword_error(self):
        """Test that calling get_results with a invalid (e.g. string) value
             will throw an error"""
        with patch('es_api.utils.queries.XDSConfiguration.objects') as \
                xdsCfg, patch('elasticsearch_dsl.Search.execute') as \
                es_execute:
            configObj = XDSConfiguration(target_xis_metadata_api="dsds",
                                         search_results_per_page=15)
            xdsCfg.first.return_value = configObj
            es_execute.return_value = {
                "test": "test"
            }

            self.assertRaises(ValueError, search_by_keyword, "test",
                              "wrong")

    def test_get_page_start_positive(self):
        """Test that calling the get_page_start returns the correct index when
            called with correct values"""
        expected_result = 40
        expected_result2 = 1
        actual_result = get_page_start(6, 8)
        actual_result2 = get_page_start(2, 1)

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(expected_result2, actual_result2)

    def test_get_page_start_negative(self):
        """Test that calling the get_page_start returns 0 when called with a
            number <= 1"""
        expected_result = 0
        expected_result2 = 0
        actual_result = get_page_start(-4, 10)
        actual_result2 = get_page_start(1, 33)

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(expected_result2, actual_result2)
