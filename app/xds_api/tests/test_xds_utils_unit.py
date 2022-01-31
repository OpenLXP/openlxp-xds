import json
from unittest.mock import patch

from configurations.models import XDSConfiguration
from core.models import CourseSpotlight, Experience
from django.test import TestCase, tag
from xds_api.utils.xds_utils import (get_spotlight_courses_api_url,
                                     metadata_to_target, save_experiences)


@tag('unit')
class UtilTests(TestCase):

    def test_get_spotlight_courses_api_url(self):
        """Test that get_spotlight_courses_api_url returns a full url using
            configured XIS api and saved spotlight courses IDs"""
        spotlight = CourseSpotlight(course_id='123')
        config = XDSConfiguration(target_xis_metadata_api="test.com/")
        expected_result = 'test.com/?metadata_key_hash_list=123'

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
                "Metadata_Ledger": {},
                "Supplemental_Ledger": {}
            },
            "unique_record_identifier": "1234",
            "metadata_key_hash": "5678"
        }

        result_list = metadata_to_target(json.dumps([metadata_dict, ]))
        result_dict = result_list
        hasMeta = "meta" in result_dict[0]

        self.assertTrue(hasMeta)
        self.assertTrue("id" in result_dict[0]["meta"])

    def test_save_experiences_empty(self):
        """Test that calling save courses on an empty list doesn't do\
            anything"""
        save_experiences([])

        self.assertEqual(len(Experience.objects.all()), 0)

    def test_save_experiences(self):
        """Test that calling save courses on a list of course hashes\
            ignores the courses that already exist and creates new ones"""
        course_1 = Experience(metadata_key_hash="123")
        course_1.save()

        save_experiences([course_1.pk, '456'])

        self.assertEqual(len(Experience.objects.all()), 2)
