from unittest.mock import patch

from configurations.models import XDSConfiguration
from core.models import Experience, InterestList, SavedFilter
from openlxp_notifications.models import email
from rest_framework.test import APITestCase
from users.models import XDSUser

from django.test import override_settings


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in XDS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        settings_manager = override_settings(SECURE_SSL_REDIRECT=False)
        settings_manager.enable()
        self.addCleanup(settings_manager.disable)

        # self.patcher = patch('users.models.email_verification')
        # self.mock_email_verification = self.patcher.start()

        self.patcher = patch('core.signals.trigger_update')
        self.mock_send_email = self.patcher.start()

        self.email_not = email(reference='Subscribed_list_update')
        self.email_not.save()

        # create user, save user, login using client
        self.auth_email = "test_auth@test.com"
        self.auth_password = "test_auth1234"
        self.auth_first_name = "first_name_auth"
        self.auth_last_name = "last_name_auth"

        XDSUser.objects.create_user(self.auth_email,
                                    self.auth_password,
                                    first_name=self.auth_first_name,
                                    last_name=self.auth_last_name,
                                    is_superuser=True)
        self.auth_user = XDSUser.objects.get(email=self.auth_email)

        self.email = "test@test.com"
        self.password = "test1234"
        self.first_name = "Jill"
        self.last_name = "doe"
        self.userDict = {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name
        }
        self.userDict_login = {
            "username": self.email,
            "password": self.password
        }

        self.userDict_login_fail = {
            "username": "test@test.com",
            "password": "test"
        }

        self.userDict_login_fail_no_username = {
            "password": "test"
        }

        self.userDict_login_fail_no_password = {
            "username": "test@test.com"
        }

        self.user_1_email = "test3@test.com"
        self.user_1_password = "1234"

        self.user_1 = XDSUser.objects.create_user(self.user_1_email,
                                                  self.user_1_password,
                                                  first_name="john",
                                                  last_name="doe")
        self.user_2 = XDSUser.objects.create_user('test2@test.com',
                                                  'test1234',
                                                  first_name='Jane',
                                                  last_name='doe')
        self.list_1 = InterestList(owner=self.user_1,
                                   name="list 1",
                                   description='list 1')
        self.list_2 = InterestList(owner=self.user_2,
                                   name="list 2",
                                   description='list 2')
        self.list_3 = InterestList(owner=self.user_2,
                                   name="list 3",
                                   description='list 3')
        self.filter_1 = SavedFilter(owner=self.user_1,
                                    name="Devops",
                                    query="randomQuery")
        self.filter_2 = SavedFilter(owner=self.user_1,
                                    name="Devops",
                                    query="randomQuery2")

        self.list_1.save()
        self.list_2.save()
        self.list_3.save()
        self.filter_1.save()
        self.filter_2.save()
        self.course_1 = Experience('1234')
        self.course_1.save()
        self.list_1.experiences.add(self.course_1)
        self.list_2.experiences.add(self.course_1)

        self.config = XDSConfiguration(target_xis_metadata_api="test")
        self.config.save()

        return super().setUp()

    def tearDown(self):
        self.patcher.stop()
        return super().tearDown()
