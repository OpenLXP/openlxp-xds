import json

from configurations.models import (CourseInformationMapping, XDSConfiguration,
                                   XDSUIConfiguration)
from core.models import SearchSortOption
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, tag
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


@tag('integration')
class ViewTests(APITestCase):

    def test_xds_ui_config_view(self):
        """Test that making a GET request to the api gives us a JSON of the
            stored XDSUIConfiguration model AND its sort options"""
        url = reverse('configurations:xds-ui-configuration')
        xds_config = XDSConfiguration(target_xis_metadata_api="test")
        xds_ui_cfg = XDSUIConfiguration(search_results_per_page=10,
                                        xds_configuration=xds_config)
        sort_option = SearchSortOption(display_name="test",
                                       field_name="test-field",
                                       xds_ui_configuration=xds_ui_cfg,
                                       active=True)
        sort_option2 = SearchSortOption(display_name="test-2",
                                        field_name="test-field-2",
                                        xds_ui_configuration=xds_ui_cfg,
                                        active=True)

        xds_config.save()
        xds_ui_cfg.save()
        sort_option.save()
        sort_option2.save()

        response = self.client.get(url)
        response_dict = json.loads(response.content)

        print(response_dict)

        self.assertEqual(response_dict['search_results_per_page'],
                         xds_ui_cfg.search_results_per_page)
        self.assertEqual(len(response_dict['search_sort_options']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@tag('integration')
class ModelTests(TestCase):

    def test_create_two_xds_configuration(self):
        """Test that trying to create more than one XDS Configuration objects
            throws ValidationError """
        with self.assertRaises(ValidationError):
            xdsConfig = XDSConfiguration(target_xis_metadata_api="test")
            xdsConfig2 = XDSConfiguration(target_xis_metadata_api="test2")
            xdsConfig.save()
            xdsConfig2.save()

    def test_xds_ui_config_rpp_validator(self):
        """Test that creating an XSD config object with a value lower than the
            min value triggers a validation error"""
        xds_config = XDSConfiguration(target_xis_metadata_api="test")
        xds_ui_config = XDSUIConfiguration(search_results_per_page=-1,
                                           xds_configuration=xds_config)
        self.assertRaises(ValidationError, xds_ui_config.full_clean)

    def test_xds_config_save_success(self):
        """Test that creating an XDS config object with correct values passes
            validation"""
        xdsConfig = XDSConfiguration(target_xis_metadata_api="test")
        xdsConfig.save()
        retrievedObj = XDSConfiguration.objects.first()

        self.assertEqual(retrievedObj.target_xis_metadata_api, "test")

    def test_save_course_information_mapping_failure(self):
        """Tests that creating more than one course mapping throws an error."""

        config = XDSConfiguration(target_xis_metadata_api="test")
        config.save()

        ui_config = XDSUIConfiguration(xds_configuration=config)
        ui_config.save()

        # course mappings
        course_title = 'Course.TestTitle'
        course_type = 'Course.CourseType'
        course_time = 'Course.EstimatedCompletionTime'
        course_description = 'Course.TestDescription'
        course_url = 'Course.TestUrl'
        course_code = 'Course.TestCode'
        course_startDate = 'Course.TestStartDate'
        course_endDate = 'Course.TestEndDate'
        course_provider = 'Course.TestProvider'
        course_instructor = 'Course.TestInstructor'
        course_deliveryMode = 'Course.TestDeliveryMode'
        course_thumbnail = 'Course.TestThumbnail'

        with self.assertRaises(IntegrityError):
            for x in range(2):
                course_information = CourseInformationMapping(
                    course_title=course_title,
                    course_description=course_description,
                    course_url=course_url,
                    course_type=course_type,
                    course_time=course_time,
                    course_code=course_code,
                    course_startDate=course_startDate,
                    course_endDate=course_endDate,
                    course_provider=course_provider,
                    course_instructor=course_instructor,
                    course_deliveryMode=course_deliveryMode,
                    course_thumbnail=course_thumbnail,
                    xds_ui_configuration=ui_config)
                # Attempting to save the data
                course_information.save()
