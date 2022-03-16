import json

from django.test import tag
from django.urls import reverse
from rest_framework import status
from users.models import XDSUser
from users.serializers import XDSUserSerializer

from .test_setup import TestSetUp


@tag('unit')
class LoginTests(TestSetUp):
    def test_login_success(self):
        """
        Test that a user can login successfully
        """

        url = reverse('users:login')

        # create a user
        XDSUser.objects.create_user(
            self.email,
            self.password,
            first_name=self.first_name,
            last_name=self.last_name,
        )

        response = self.client.post(url, self.userDict_login, format='json')

        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(responseDict['user'] is not None)

    def test_login_no_user_fail(self):
        """
        Test that a user can not login with a non-existent user
        """

        url = reverse('users:login')

        response = self.client.post(url, self.userDict_login, format='json')

        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(responseDict['info'], 'User does not exist')

    def test_login_no_username_fail(self):
        """
        Test that a user can not login with a non-existent username
        """

        url = reverse('users:login')

        response = self.client.post(url,
                                    self.userDict_login_fail_no_username,
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_no_password_fail(self):
        """
        Test that a user can not login with a non-existent password
        """

        url = reverse('users:login')

        response = self.client.post(
            url, self.userDict_login_fail_no_password, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_is_logged_in_success(self):
        """
        Test that calling /api/auth/validate with a user sessionid returns a
         200 response
        """
        url = reverse('users:validate')

        # log the user in
        self.client.login(email=self.auth_email, password=self.auth_password)

        # verify the user is logged in
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_is_logged_in_fail(self):
        """
        Test that calling /api/auth/validate returns a unauthorized error
        """
        url = reverse('users:validate')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        """Test that calling /api/auth/logout returns a success message"""
        url = reverse('users:logout')

        # login
        self.client.login(email=self.email, password=self.password)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


@tag('unit')
class RegisterTests(TestSetUp):
    def test_register_view(self):
        """
        Test the registration
        """

        # url
        url = reverse('users:register')

        response = self.client.post(url, self.userDict, format="json")

        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(responseDict['user'] is not None)

    def test_no_username_register(self):
        """
        Test fails when no username
        """
        url = reverse('users:register')

        response = self.client.post(
            url, {'password': self.password, 'first_name': self.first_name,
                  'last_name': self.last_name}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_repeated_username_register(self):
        """
        Test fails when reusing username
        """
        url = reverse('users:register')

        response = self.client.post(
            url, {'password': self.password, 'first_name': self.first_name,
                  'last_name': self.last_name, 'email': self.auth_email},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@tag('unit')
class ValidateTests(TestSetUp):
    def test_correct_validate(self):
        """Test that the validate endpoint verifies an active session"""
        url_validate = reverse('users:validate')

        self.client.login(username=self.user_1_email,
                          password=self.user_1_password)

        validate_dict = {"user": XDSUserSerializer(self.user_1).data}

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            json.loads(validate_response.content.decode('utf-8')),
            validate_dict)

    def test_no_session_validate(self):
        """Test that the validate endpoint errors when no active session"""
        url_validate = reverse('users:validate')

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code,
                         status.HTTP_401_UNAUTHORIZED)


@tag('unit')
class LogoutTests(TestSetUp):
    def test_correct_logout(self):
        """Test that the logout endpoint ends a session and logs out"""
        url = reverse('users:logout')
        url_validate = reverse('users:validate')

        self.client.login(username=self.user_1_email,
                          password=self.user_1_password)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code,
                         status.HTTP_401_UNAUTHORIZED)
