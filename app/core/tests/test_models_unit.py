from configurations.models import XDSConfiguration
from core.models import (CourseDetailHighlight, CourseSpotlight, Experience,
                         InterestList, SearchFilter, SearchSortOption,
                         XDSUIConfiguration, SearchField)
from django.test import tag
from users.models import XDSUser

from .test_setup import TestSetUp


@tag('unit')
class ModelTests(TestSetUp):

    def test_create_search_filter(self):
        """Test that creating a search filter object works correctly"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)
        sf = SearchFilter(display_name="test",
                          field_name="test",
                          xds_ui_configuration=uiConfig)
        self.assertEqual(sf.xds_ui_configuration, uiConfig)
        self.assertEqual(str(sf), str(sf.id))

    def test_create_search_sort_option(self):
        """Test that creating a search sort option works as expected"""
        name = "test name"
        field = "test.name"
        sort_option = SearchSortOption(display_name=name,
                                       field_name=field)
        self.assertEqual(name, sort_option.display_name)
        self.assertEqual(field, sort_option.field_name)
        self.assertTrue(sort_option.active)
        self.assertEqual(str(sort_option), str(sort_option.id))

    def test_create_search_field(self):
        """Test that creating a search sort option works as expected"""
        name = "test name"
        field = "test.name"
        search_field = SearchField(display_name=name,
                                   field_name=field)
        self.assertEqual(name, search_field.display_name)
        self.assertEqual(field, search_field.field_name)
        self.assertTrue(search_field.active)
        self.assertEqual(str(search_field), str(search_field.id))

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
        self.assertEqual(str(courseHighlight), str(courseHighlight.id))

    def test_create_courseSpotlight(self):
        """Test the creation of a course spotlight object"""
        c_id = "12345"
        spotlight = CourseSpotlight(course_id=c_id)

        self.assertEqual(c_id, spotlight.course_id)
        self.assertTrue(spotlight.active)
        self.assertEqual(str(spotlight), str(spotlight.id))

    def test_create_experience(self):
        """Tests that creating a course is successful"""
        id = '12345'
        course = Experience(metadata_key_hash=id)
        course.save()
        savedCourse = Experience.objects.get(pk=id)
        self.assertEqual(course.metadata_key_hash,
                         savedCourse.metadata_key_hash)

    def test_create_interest_list_existing_course(self):
        """Tests that creating an interest list with existing courses works"""
        id = '12345'
        course = Experience(metadata_key_hash=id)
        course.save()
        user = XDSUser.objects.create_user(self.email,
                                           self.password,
                                           first_name=self.first_name,
                                           last_name=self.last_name)
        list = InterestList(owner=user,
                            name="test list",
                            description="test desc")
        list.save()
        list.experiences.add(course)

        # check that course is found in the interest list's list of courses
        for currCourse in list.experiences.all():
            self.assertEqual(course, currCourse)
