import json
from unittest.mock import patch

from django.test import SimpleTestCase, tag

from es_api.utils.queries import get_results, more_like_this


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
        # Test that calling more_like_this returns whatever response elastic
        # search returns
        with patch('elasticsearch_dsl.Search.execute') as es_execute:
            resultVal = {
                "test": "test"
            }
            es_execute.return_value = {
                "test": "test"
            }
            result = more_like_this(1)
            self.assertEqual(result, resultVal)
