from configurations.models import XDSConfiguration, XDSUIConfiguration
from core.models import CourseDetailHighlight, CourseInformationMapping
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, tag


@tag('integration')
class ModelTests(TestCase):

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

    def test_save_course_information_mapping_failure(self):
        """Tests that creating more than one course mapping throws an error."""

        config = XDSConfiguration(target_xis_metadata_api="test")
        config.save()

        ui_config = XDSUIConfiguration(xds_configuration=config)
        ui_config.save()

        # course mappings
        course_title = 'Course.TestTitle'
        course_description = 'Course.TestDescription'
        course_url = 'Course.TestUrl'
        with self.assertRaises(IntegrityError):
            for x in range(2):
                course_information = CourseInformationMapping(
                    course_title=course_title,
                    course_description=course_description,
                    course_url=course_url,
                    xds_ui_configuration=ui_config)
                # Attempting to save the data
                course_information.save()
