from unittest.mock import patch
from django.test import SimpleTestCase
from django.test import tag
from es_api.utils.queries import get_results
import json


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
