import json
from unittest.mock import patch

from configurations.models import (CourseInformationMapping, XDSConfiguration,
                                   XDSUIConfiguration)
from django.contrib.auth.models import Group
from django.test import tag
from django.urls import reverse
from rest_framework import status
from users.models import Organization, XDSUser

from .test_setup import TestSetUp


@tag('unit')
class ConfigurationTests(TestSetUp):

    def test_xds_ui_config_view(self):
        """Test that making a GET request to the api gives us a JSON of the
            stored XDSUIConfiguration model"""
        url = reverse('configurations:xds-ui-configuration')
        with patch('configurations.views.XDSUIConfiguration.objects') \
                as xds_ui_Obj:
            xds_config = XDSConfiguration(target_xis_metadata_api="test")
            xds_ui_cfg = XDSUIConfiguration(search_results_per_page=10,
                                            xds_configuration=xds_config)
            xds_ui_Obj.return_value = xds_ui_Obj
            xds_ui_Obj.first.return_value = xds_ui_cfg

            response = self.client \
                .get(url)
            response_dict = json.loads(response.content)

            self.assertEqual(response_dict['search_results_per_page'],
                             xds_ui_cfg.search_results_per_page)
            self.assertEqual(response_dict['search_sort_options'], [])
            self.assertEqual(response_dict['course_highlights'], [])
            self.assertEqual(response_dict['single_sign_on_options'], [])
            self.assertEqual(response.status_code, status.HTTP_200_OK)


@tag('unit')
class ModelTests(TestSetUp):
    def test_create_xds_configuration(self):
        """Test that creating a new XDS Configuration entry is successful\
        with defaults """
        xdsConfig = XDSConfiguration(target_xis_metadata_api="test")

        self.assertEqual(xdsConfig.target_xis_metadata_api, "test")
        self.assertEqual(str(xdsConfig), str(xdsConfig.id))

    def test_create_xds_ui_configuration(self):
        """Test that creating a new XDSUI Configuration is successful with \
            defaults"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)

        self.assertEqual(uiConfig.search_results_per_page, 10)
        self.assertEqual(str(uiConfig), str(uiConfig.id))

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
        self.assertEqual(str(courseInformation), str(courseInformation.id))

    def test_default_user_group(self):
        """Test that default_user_group is used when defined"""
        group = Group.objects.create(name="test")
        XDSConfiguration.objects.update(default_user_group=group)
        username = "testUser@test.com"
        password = "pass123"
        f_name = "Basic"
        l_name = "User"
        xdsuser = XDSUser.objects.create_user(
            username, password, first_name=f_name, last_name=l_name)

        self.assertIn(group, xdsuser.groups.all())
        self.assertEqual(len(xdsuser.groups.all()), 1)

    def test_create_organizations(self):
        """Test that Organizations are created when updating the config"""
        orgs = ["ABC", "XYZ", "LMN"]
        with patch("configurations.models.BaseQueries") as bq:
            bq().filter_options.return_value = orgs
            XDSConfiguration.objects.first().save()

            for o in Organization.objects.all():
                self.assertIn(o.name, orgs)
            self.assertEqual(len(Organization.objects.all()), len(orgs))
