from rest_framework.test import APITestCase


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in XDS"""

    def setUp(self):
        """Function to set up necessary data for testing"""
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
        return super().tearDown()
