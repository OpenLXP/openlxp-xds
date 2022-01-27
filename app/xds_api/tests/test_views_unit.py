import json
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import tag
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from requests.exceptions import HTTPError, RequestException
from rest_framework import status

from core.models import CourseSpotlight, SavedFilter
from configurations.models import XDSConfiguration

from .test_setup import TestSetUp


@tag('unit')
class InterestListsTests(TestSetUp):
    def test_interest_lists_unauthenticated(self):
        """
        Test that an unauthenticated user can not fetch any interest lists
        Endpoint: /api/interest_lists
        """
        url = reverse('xds_api:interest-lists')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_interest_lists_authenticated(self):
        """
        Test that an authenticated user only gets their created interest lists
        when calling the /api/interest-lists api
        """
        url = reverse('xds_api:interest-lists')

        # login user
        self.client.login(email=self.auth_email, password=self.auth_password)

        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict[0]["owner"]["email"], self.user_1.email)

    def test_interest_lists_not_valid_authenticated(self):
        """
        Test that an http error 400 occurs when no data is provided
        """

        url = reverse('xds_api:interest-lists')

        # login user
        self.client.login(email=self.auth_email, password=self.auth_password)

        with patch('xds_api.views.InterestListsView') as mock:
            mock.side_effect = Exception

            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_interest_list_unauthenticated(self):
        """
        Test that an unauthenticated user can not create an interest list.
        """
        url = reverse('xds_api:interest-lists')

        # create interest list
        interest_list_data = {
            "name": "Test Interest List",
            "description": "Test Description",
        }

        response = self.client.post(url, interest_list_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_interest_list_authenticated(self):
        """
        Test that an authenticated user can create an interest list.
        """
        url = reverse('xds_api:interest-lists')

        # login user
        self.client.login(email=self.auth_email, password=self.auth_password)

        # create interest list
        interest_list_data = {
            "name": "Test Interest List",
            "description": "Test Description",
            "courses": []
        }

        response = self.client.post(url, interest_list_data, format="json")
        response_dict = json.loads(response.content)
        print(response_dict)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_dict["name"], "Test Interest List")

    def test_get_interest_list_unauthenticated(self):
        """
        Test that an unauthenticated user can not get an interest list.
        """

        list_id = '1234'
        url = reverse('xds_api:interest-list', args=(list_id,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_interest_list_authenticated(self):
        """
        Test that an authenticated user can get an interest list by id.
        """
        list_id = self.list_3.pk
        url = reverse('xds_api:interest-list', args=(list_id,))

        # login user
        self.client.login(email=self.auth_email, password=self.auth_password)

        response = self.client.get(url)
        response_dict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_dict["name"], self.list_3.name)

    def test_get_interest_list_with_courses_authenticated(self):
        """
        Test that an authenticated user can get an interest list by id,
        and the list has a formatted course.
        """

        list_id = self.list_1.pk
        url = reverse('xds_api:interest-list', args=(list_id,))

        # login user
        self.client.login(email=self.auth_email, password=self.auth_password)

        with patch('xds_api.views.get_request') as get_request, \
                patch('configurations.views.XDSConfiguration.objects') \
                as conf_obj:
            # mock the configuration object
            conf_obj.return_value = conf_obj
            conf_obj.first.return_value = \
                XDSConfiguration(target_xis_metadata_api="www.test.com")

            # mock the get request
            mock_response = get_request.return_value
            mock_response.status_code = 200
            mock_response.json.return_value = [{
                "test": "value",
            }]

            # re-assign the mock to the get request
            get_request.return_value = mock_response

            response = self.client.get(url)
            responseDict = json.loads(response.content)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(responseDict["experiences"], [None])

    def test_get_interest_list_by_id_no_xis(self):
        """
        Test that an authenticated user can get an interest list by id,
        and the list has a formatted course.
        """

        list_id = self.list_1.pk
        url = reverse('xds_api:interest-list', args=(list_id,))

        # login user
        self.client.login(email=self.auth_email, password=self.auth_password)

        with patch('xds_api.views.get_request') as get_request, \
                patch('configurations.views.XDSConfiguration.objects') \
                as conf_obj:
            # mock the configuration object
            conf_obj.return_value = conf_obj
            conf_obj.first.return_value = \
                XDSConfiguration(target_xis_metadata_api="www.test.com")

            # mock the get request
            mock_response = get_request.return_value
            mock_response.status_code = 500
            mock_response.json.return_value = [{
                "test": "value",
            }]

            # re-assign the mock to the get request
            get_request.return_value = mock_response

            response = self.client.get(url)

            self.assertEqual(response.status_code,
                             status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_get_interest_list_by_id_not_found(self):
        """
        Test that requesting an interest list by ID using the
        /api/interest-lists/id api returns an error if none is found
        """
        id = '1234'
        self.client.login(email=self.auth_email, password=self.auth_password)
        url = reverse('xds_api:interest-list', args=(id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_interest_list_unauthenticated(self):
        """
        Test that an unauthenticated user cannot edit an interest list.
        """
        list_id = self.list_1.pk
        url = reverse('xds_api:interest-list', args=(list_id,))

        response = self.client.patch(url, {'name': 'new name'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_interest_list_authenticated_not_owner(self):
        """
        Test that an authenticated user cannot edit an interest list that is
        not theirs.
        """
        list_id = self.list_2.pk
        url = reverse('xds_api:interest-list', args=(list_id,))

        # login user
        self.client.login(email=self.auth_email, password=self.auth_password)

        response = self.client.patch(url, {'name': 'new name'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_interest_list_authenticated_owner(self):
        """
        Test that an authenticated user can edit an interest list that
        is theirs.
        """
        list_id = self.list_1.id
        url = reverse('xds_api:interest-list', args=(list_id,))

        new_name = "edited name"
        empty_list = []
        new_list = {"name": new_name,
                    "description": self.list_1.description,
                    "experiences": empty_list}

        cont_type = ContentType.objects.get(app_label='xds_api',
                                            model='interestlist')
        permission = Permission.objects. \
            get(name='Can change interest list', content_type=cont_type)
        self.user_1.user_permissions.add(permission)
        self.client.login(email=self.user_1_email,
                          password=self.user_1_password)

        response = \
            self.client.patch(url,
                              data=json.dumps(new_list),
                              content_type="application/json")
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict["name"], new_name)
        self.assertEqual(responseDict["experiences"], [])

    def test_edit_interest_list_authenticated_invalid_change(self):
        """
        Test that an authenticated user making an invlid change to a
        list returns a 400.
        """
        list_id = self.list_1.id
        url = reverse('xds_api:interest-list', args=(list_id,))

        empty_list = []
        new_list = {"description": self.list_1.description,
                    "experiences": empty_list}

        cont_type = ContentType.objects.get(app_label='xds_api',
                                            model='interestlist')
        permission = Permission.objects. \
            get(name='Can change interest list', content_type=cont_type)
        self.user_1.user_permissions.add(permission)
        self.client.login(email=self.user_1_email,
                          password=self.user_1_password)

        response = \
            self.client.patch(url,
                              data=json.dumps(new_list),
                              content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_interest_list_unauthenticated(self):
        """
        Test that an unauthenticated user cannot delete an interest list.
        """
        list_id = self.list_1.pk
        url = reverse('xds_api:interest-list', args=(list_id,))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_interest_list_authenticated_not_owner(self):
        """
        Test that an authenticated user cannot delete an interest list
        that is not theirs.
        """
        list_id = self.list_2.pk
        url = reverse('xds_api:interest-list', args=(list_id,))

        # login user
        self.client.login(email=self.auth_email, password=self.auth_password)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_interest_list_authenticated_owner(self):
        """
        Test that an authenticated user can delete an interest list
        that is theirs.
        """
        list_id = self.list_1.id
        url = reverse('xds_api:interest-list', args=(list_id,))

        cont_type = ContentType.objects.get(app_label='xds_api',
                                            model='interestlist')
        permission = Permission.objects. \
            get(name='Can delete interest list', content_type=cont_type)
        self.user_1.user_permissions.add(permission)
        self.client.login(email=self.user_1_email,
                          password=self.user_1_password)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_course_multiple_lists_unauthenticated(self):
        """
        Test that an unauthenticated user cannot add a course to a list.
        """
        list_id = self.list_1.pk
        url = reverse('xds_api:add_course_to_lists', args=(list_id,))

        response = self.client.post(url, {'name': 'new name'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_course_multiple_lists_success(self):
        """
        Test that adding a course to multiple lists is successful when
        user is owner for the /api/add-course-to-lists POST api
        """
        course_id = self.course_1.pk
        url = reverse('xds_api:add_course_to_lists', args=(course_id,))
        permission = Permission.objects. \
            get(name='Can add add course to lists')
        self.user_2.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_2)
        data = {
            "lists": [self.list_3.pk]
        }
        response = \
            self.client.post(url,
                             data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.list_3.experiences.all()), 1)

    def test_get_owned_interest_lists_auth(self):
        """Test that an authenticated user only gets their created interest
            lists when calling the /api/interest-lists/owned api"""
        url = reverse('xds_api:owned-lists')
        permission = Permission.objects. \
            get(name='Can view interest lists owned')
        self.user_1.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_1)
        response = self.client \
            .get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict[0]["owner"]["email"], self.user_1.email)
        self.assertEqual(len(self.user_1.interest_lists.all()),
                         len(responseDict))

    def test_get_subscriptions_auth(self):
        """Test that an authenticated user can get a list of interest lists
            that they are subscribed to when calling the endpoint
            /api/interest-lists/subscriptions"""
        url = reverse('xds_api:interest-list-subscriptions')
        permission = Permission.objects. \
            get(name='Can view interest lists subscriptions')
        self.user_1.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_1)
        # subscribe user 1 to interest list 3
        self.list_3.subscribers.add(self.user_1)
        self.list_3.save()
        response = self.client \
            .get(url)
        response_dict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.list_3.subscribers.all()),
                         len(response_dict))

    def test_interest_list_subscribe(self):
        """Test that an authenticated user can subscribe to an interest list
            when calling the endpoint /api/interest-lists/<id>/subscribe"""
        list_id = self.list_2.pk
        url = reverse('xds_api:interest-list-subscribe', args=(list_id,))
        permission = Permission.objects. \
            get(name='Can change interest list subscribe')
        self.user_1.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_1)
        response = self.client \
            .patch(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.list_2.subscribers.all()), 1)

    def test_interest_list_unsubscribe(self):
        """Test that an authenticated user can unsubscribe to an interest list
            when calling the endpoint /api/interest-lists/<id>/unsubscribe"""
        list_id = self.list_2.pk
        url = reverse('xds_api:interest-list-unsubscribe', args=(list_id,))
        permission = Permission.objects. \
            get(name='Can change interest list unsubscribe')
        self.user_1.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_1)
        # subscribe user 1 to interest list 3
        self.list_2.subscribers.add(self.user_1)
        self.list_2.save()
        response = self.client \
            .patch(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.list_2.subscribers.all()), 0)


@tag('unit')
class SavedFiltersTests(TestSetUp):
    def test_get_saved_filters_owned_unauthorized(self):
        """Test that an unauthenticated user cannot get a list of their
            saved filters when calling the endpoint
            /api/interest-lists/saved-filters/owned"""
        url = reverse('xds_api:owned-filters')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_saved_filters_owned_authorized(self):
        """
        Test that a user can view their saved filters
        """
        url = reverse('xds_api:owned-filters')
        permission = Permission.objects. \
            get(name='Can view saved filters owned')
        self.user_1.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.user_1.saved_filters.all()), 2)

    def test_get_saved_filters(self):
        """Test that trying to get saved filter through the
            /api/saved-filters api succeeds"""
        url = reverse('xds_api:saved-filters')

        saved_config = SavedFilter(owner=self.user_1,
                                   name="Devops", query="randomQuery")
        saved_config.save()
        permission = Permission.objects. \
            get(name='Can view saved filters')
        self.user_1.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_1)
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict[0]["name"], "Devops")

    def test_create_saved_filters_owned_authorized(self):
        """Test that trying to create saved filter through the
            /api/saved-filters api succeeds"""
        url = reverse('xds_api:saved-filters')
        saved_filter = {
            "name": "Devops",
            "query": "randomQuery"
        }
        permission = Permission.objects. \
            get(name='Can add saved filters')
        self.user_1.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_1)
        response = \
            self.client.post(url,
                             saved_filter)
        response_dict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED),
        self.assertEqual(response_dict["name"], "Devops")

    def test_create_saved_filters_owned_invalid_authorized(self):
        """
        Test that trying to create saved filter through the
        /api/saved-filters api fails with an invalid query
        """
        url = reverse('xds_api:saved-filters')
        saved_filter = {
            "query": "randomQuery"
        }
        permission = Permission.objects. \
            get(name='Can add saved filters')
        self.user_1.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_1)
        response = \
            self.client.post(url,
                             saved_filter)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST),

    def test_create_saved_filters_no_auth(self):
        """Test that trying to create a saved filter through the
            /api/saved-filters api returns an error"""
        url = reverse('xds_api:saved-filters')
        saved_filter = {
            "name": "Devops",
            "query": "randomQuery"
        }

        response = self.client.post(url, saved_filter)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_saved_filter_unauthorized(self):
        """Test that an unauthenticated user cannot get a saved filter
            when calling the endpoint /api/interest-lists/saved-filters/<id>"""
        url = reverse('xds_api:saved-filter', args=(self.filter_1.pk,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_saved_filter_authorized(self):
        """Test that trying to get saved filter through the
            /api/saved-filter api succeeds"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))

        cont_type = ContentType.objects.get(app_label='xds_api',
                                            model='savedfilter')
        permission = Permission.objects. \
            get(name='Can view saved filter', content_type=cont_type)
        self.user_1.user_permissions.add(permission)
        self.client.login(email=self.user_1_email,
                          password=self.user_1_password)

        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict["name"], "Devops")

    def test_edit_saved_filter_not_owner(self):
        """Test that users cannot made edits to filters they do not own
        using the /api/saved-filter/id PATCH"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        self.client.login(email=self.auth_email, password=self.auth_password)
        response = \
            self.client.patch(url,
                              data={"test": "test"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_saved_filter_unauthorized(self):
        """Test that unauthenticated users cannot made edits to filters
        using the /api/saved-filter/id PATCH"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        self.client.login(email=self.auth_email, password=self.auth_password)
        response = self.client.patch(url, data={"test": "test"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_saved_filter_invalid_authorized(self):
        """Test that trying to edit a saved filter through the"""

        filter_id = self.filter_1.pk
        edit_filter = {
            "name": "Devops",
        }

        url = reverse('xds_api:saved-filter', args=(filter_id,))
        cont_type = ContentType.objects.get(app_label='xds_api',
                                            model='savedfilter')
        permission = Permission.objects. \
            get(codename='change_savedfilter', content_type=cont_type)
        self.user_1.user_permissions.add(permission)
        self.client.login(email=self.user_1_email,
                          password=self.user_1_password)

        response = self.client.patch(url, data=edit_filter)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_saved_filter_success(self):
        """Test that editing an filter is successful using the \
            /api/saved-filter/id PATCH"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        cont_type = ContentType.objects.get(app_label='xds_api',
                                            model='savedfilter')
        permission = Permission.objects. \
            get(name='Can change saved filter', content_type=cont_type)
        self.user_1.user_permissions.add(permission)
        self.client.force_authenticate(user=self.user_1)
        new_name = "edited name"
        new_list = {"name": new_name,
                    "query": self.filter_2.query
                    }
        response = \
            self.client.patch(url,
                              data=json.dumps(new_list),
                              content_type="application/json")
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict["name"], new_name)
        self.assertEqual(responseDict["query"], self.filter_2.query)

    def test_delete_saved_filter_not_owner(self):
        """Test that users cannot remove filters they do not own
        using the /api/saved-filter/id DELETE"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        self.client.login(email=self.auth_email, password=self.auth_password)
        response = \
            self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_saved_filter_success(self):
        """Test that removing an filter is successful using the \
            /api/saved-filter/id DELETE"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        cont_type = ContentType.objects.get(app_label='xds_api',
                                            model='savedfilter')
        permission = Permission.objects. \
            get(name='Can delete saved filter', content_type=cont_type)
        self.user_1.user_permissions.add(permission)
        self.client.login(email=self.user_1_email,
                          password=self.user_1_password)

        response = \
            self.client.delete(url,
                               content_type="application/json")
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(responseDict["message"])


@tag('unit')
class SpotlightCoursesTests(TestSetUp):
    def test_get_spotlight_courses(self):
        """test that calling the endpoint /api/spotlight-courses returns a
            list of documents for configured spotlight courses"""
        url = reverse('xds_api:spotlight-courses')

        permission = Permission.objects. \
            get(name='Can view get spotlight courses')
        self.auth_user.user_permissions.add(permission)

        self.client.login(email=self.auth_email, password=self.auth_password)

        with patch('xds_api.views.get_request') as get_request, \
                patch('xds_api.views.'
                      'get_spotlight_courses_api_url') as get_api_url:
            get_api_url.return_value = "www.test.com"
            http_resp = get_request.return_value
            get_request.return_value = http_resp
            http_resp.json.return_value = [{
                "test": "value"
            }]
            http_resp.status_code = 200

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_spotlight_courses_error(self):
        """test that calling the endpoint /api/spotlight-courses returns an
            http error if an exception a thrown while reaching out to XIS"""
        url = reverse('xds_api:spotlight-courses')
        errorMsg = "error reaching out to configured XIS API; " + \
                   "please check the XIS logs"
        permission = Permission.objects. \
            get(name='Can view get spotlight courses')
        self.auth_user.user_permissions.add(permission)
        self.client.login(email=self.auth_email, password=self.auth_password)
        CourseSpotlight(course_id='abc123').save()

        with patch('xds_api.views.get_request') as get_request, \
                patch('xds_api.views.'
                      'get_spotlight_courses_api_url') as get_api_url:
            get_api_url.return_value = "www.test.com"
            get_request.side_effect = [HTTPError]

            response = self.client.get(url)
            responseDict = json.loads(response.content)

            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(responseDict['message'], errorMsg)

    def test_get_spotlight_courses_empty(self):
        """test that calling the endpoint /api/spotlight-courses returns
            nothing if there are no spotlight courses"""
        url = reverse('xds_api:spotlight-courses')
        permission = Permission.objects. \
            get(name='Can view get spotlight courses')
        self.auth_user.user_permissions.add(permission)
        self.client.login(email=self.auth_email, password=self.auth_password)

        with patch('xds_api.views.get_request'), \
                patch('xds_api.views.'
                      'get_spotlight_courses_api_url'):

            response = self.client.get(url)

            self.assertEqual(response.status_code,
                             status.HTTP_200_OK)
            self.assertEqual(len(response.content), 0)


@tag('unit')
class ViewTests(TestSetUp):

    def test_get_experiences_server_error(self):
        """Test that calling the endpoint /api/experiences returns an
            http error if an exception a thrown while reaching out to XIS"""
        doc_id = '123456'
        url = reverse('xds_api:get_courses', args=(doc_id,))
        errorMsg = "error reaching out to configured XIS API; " + \
                   "please check the XIS logs"
        self.client.login(email=self.auth_email, password=self.auth_password)
        with patch('xds_api.views.get_request') as get_request:
            get_request.side_effect = RequestException

            response = self.client.get(url)
            responseDict = json.loads(response.content)

            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(responseDict['message'], errorMsg)

    def test_get_experiences_not_found(self):
        """
        Test that calling /api/experiences returns an http 404 error when
        a course is not found.
        """
        doc_id = '123456'
        url = reverse('xds_api:get_courses', args=(doc_id,))

        # login user and get token
        self.client.login(email=self.auth_email, password=self.auth_password)

        with patch('xds_api.views.get_request') as get_request:
            get_request.side_effect = ObjectDoesNotExist

            response = self.client.get(url)

            self.assertEqual(response.status_code,
                             status.HTTP_404_NOT_FOUND)
