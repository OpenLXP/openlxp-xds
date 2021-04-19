from django.core.exceptions import ValidationError
from django.test import TestCase, tag

from core.models import (CourseDetailHighlight, XDSConfiguration,
                         XDSUIConfiguration)


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

    def test_course_detail_highlight_rpp_validator(self):
        """Test that creating Course Detail Highlight with an invalid rank
            value fails validation"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)
        highlight_icon = "clock"
        name = "test"
        field = "test.field"
        courseHighlight = CourseDetailHighlight(display_name=name,
                                                field_name=field,
                                                xds_ui_configuration=uiConfig,
                                                highlight_icon=highlight_icon,
                                                rank=0)
        self.assertRaises(ValidationError, courseHighlight.full_clean)

    def test_save_course_detail_highlight_fail(self):
        """Test that creating more than 8 active course detail highlights
            throws an error"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)
        highlight_icon = "clock"
        name = "test"
        field = "test.field"

        config.save()
        uiConfig.save()

        with self.assertRaises(ValidationError):
            for x in range(9):
                courseHighlight = \
                    CourseDetailHighlight(display_name=name,
                                          field_name=field,
                                          xds_ui_configuration=uiConfig,
                                          highlight_icon=highlight_icon,
                                          rank=0)
                courseHighlight.save()

    def test_save_course_detail_highlight_success(self):
        """Test that creating a simple course detail highlight is successful"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)
        highlight_icon = "clock"
        name = "test"
        field = "test.field"
        courseHighlight = CourseDetailHighlight(display_name=name,
                                                field_name=field,
                                                xds_ui_configuration=uiConfig,
                                                highlight_icon=highlight_icon)

        config.save()
        uiConfig.save()
        courseHighlight.save()
        retrievedObj = CourseDetailHighlight.objects.first()

        self.assertEqual(retrievedObj.field_name, field)
        self.assertEqual(retrievedObj.display_name, name)
