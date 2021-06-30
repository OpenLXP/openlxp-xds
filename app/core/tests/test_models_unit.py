from django.test import SimpleTestCase, tag

from core.models import (CourseDetailHighlight, CourseInformationMapping,
                         CourseSpotlight, SearchFilter, SearchSortOption,
                         XDSConfiguration, XDSUIConfiguration)


@tag('unit')
class ModelTests(SimpleTestCase):

    def test_create_xds_configuration(self):
        """Test that creating a new XDS Configuration entry is successful\
        with defaults """
        xdsConfig = XDSConfiguration(target_xis_metadata_api="test")

        self.assertEqual(xdsConfig.target_xis_metadata_api, "test")

    def test_create_xds_ui_configuration(self):
        """Test that creating a new XDSUI Configuration is successful with \
            defaults"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)

        self.assertEqual(uiConfig.search_results_per_page, 10)

    def test_create_search_filter(self):
        """Test that creating a search filter object works correctly"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)
        sf = SearchFilter(display_name="test",
                          field_name="test",
                          xds_ui_configuration=uiConfig)
        self.assertEqual(sf.xds_ui_configuration, uiConfig)

    def test_create_search_sort_option(self):
        """Test that creating a search sort option works as expected"""
        name = "test name"
        field = "test.name"
        sort_option = SearchSortOption(display_name=name,
                                       field_name=field)
        self.assertEqual(name, sort_option.display_name)
        self.assertEqual(field, sort_option.field_name)
        self.assertTrue(sort_option.active)

    def test_create_course_detail_highlight(self):
        """Test creating a course detail highlight object"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)
        highlight_icon = "clock"
        name = "test"
        field = "test.field"
        active = False
        courseHighlight = CourseDetailHighlight(display_name=name,
                                                field_name=field,
                                                xds_ui_configuration=uiConfig,
                                                active=active,
                                                highlight_icon=highlight_icon)

        self.assertEqual(courseHighlight.display_name, name)
        self.assertEqual(courseHighlight.field_name, field)
        self.assertEqual(courseHighlight.highlight_icon, highlight_icon)
        self.assertEqual(courseHighlight.rank, 1)
        self.assertEqual(courseHighlight.active, active)

    def test_create_courseSpotlight(self):
        """Test the creation of a course spotlight object"""
        c_id = "12345"
        spotlight = CourseSpotlight(course_id=c_id)

        self.assertEqual(c_id, spotlight.course_id)
        self.assertTrue(spotlight.active)

    def test_create_courseInformationMapping(self):
        """Tests the creation of a course information object"""

        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)

        # course mappings
        course_title = 'Course.TestTitle'
        course_description = 'Course.TestDescription'
        course_url = 'Course.TestUrl'

        courseInformation = CourseInformationMapping(
            xds_ui_configuration=uiConfig,
            course_title=course_title,
            course_description=course_description,
            course_url=course_url)

        self.assertEqual(courseInformation.course_title, course_title)
        self.assertEqual(courseInformation.course_description,
                         course_description)
        self.assertEqual(courseInformation.course_url, course_url)
