from unittest.mock import patch

from openlxp_notifications.models import email
from rest_framework.test import APITestCase

from django.test import override_settings


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in XDS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        settings_manager = override_settings(SECURE_SSL_REDIRECT=False)
        settings_manager.enable()
        self.addCleanup(settings_manager.disable)

        self.patcher = patch('core.signals.trigger_update')
        self.mock_send_email = self.patcher.start()

        self.email_not = email(reference='Subscribed_list_update')
        self.email_not.save()

        self.email = "test@test.com"
        self.password = "test1234"
        self.first_name = "john"
        self.last_name = "doe"
        self.userDict = {
            "email": "test@test.com",
            "password": "test1234",
            "first_name": "john",
            "last_name": "doe"
        }
        self.userDict_login = {
            "username": "test@test.com",
            "password": "test1234"
        }

        self.userDict_login_fail = {
            "username": "test@test.com",
            "password": "test"
        }

        return super().setUp()

    def tearDown(self):
        self.patcher.stop()
        return super().tearDown()
