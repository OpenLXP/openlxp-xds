import json
from unittest.mock import patch

from django.test import SimpleTestCase, tag

from core.models import CourseSpotlight, XDSConfiguration
from xds_api.utils.xds_utils import (get_spotlight_courses_api_url,
                                     metadata_to_target)


@tag('unit')
class UtilTests(SimpleTestCase):

    def test_get_spotlight_courses_api_url(self):
        """Test that get_spotlight_courses_api_url returns a full url using
            configured XIS api and saved spotlight courses IDs"""
        spotlight = CourseSpotlight(course_id='123')
        config = XDSConfiguration(target_xis_metadata_api="test.com/")
        expected_result = 'test.com/?id=123'

        with patch('xds_api.utils.xds_utils.CourseSpotlight.objects') as \
            courseSpotlight, patch('xds_api.utils.xds_utils'
                                   '.XDSConfiguration.objects') as xdsConfig:
            courseSpotlight.return_value = courseSpotlight
            xdsConfig.return_value = xdsConfig
            courseSpotlight.filter.return_value = [spotlight, ]
            xdsConfig.first.return_value = config

            actual_result = get_spotlight_courses_api_url()

            self.assertEqual(expected_result, actual_result)

    def test_metadata_to_target(self):
        """Test that given a course/record JSON, calling metadata_to_target
            returns a JSON object similar to { "meta": {"id": "1234"}, ...}"""
        metadata_dict = {
            "metadata": {
                "test": "test"
            },
            "unique_record_identifier": "1234"
        }

        result_list = metadata_to_target(json.dumps([metadata_dict, ]))
        result_dict = json.loads(result_list)
        hasMeta = "meta" in result_dict[0]

        self.assertTrue(hasMeta)
        self.assertTrue("id" in result_dict[0]["meta"])
