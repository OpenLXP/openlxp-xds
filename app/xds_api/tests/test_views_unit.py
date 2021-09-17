import json
from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from knox.models import AuthToken
from requests.exceptions import HTTPError, RequestException
from rest_framework import status

from core.models import (SavedFilter, XDSConfiguration, XDSUIConfiguration,
                         XDSUser)

from .test_setup import TestSetUp


@tag('unit')
class ViewTests(TestSetUp):

    def test_xds_ui_config_view(self):
        """Test that making a GET request to the api gives us a JSON of the
            stored XDSUIConfiguration model"""
        url = reverse('xds_api:xds-ui-configuration')
        with patch('xds_api.views.XDSUIConfiguration.objects') as xds_ui_Obj:
            xds_config = XDSConfiguration(target_xis_metadata_api="test")
            xds_ui_cfg = XDSUIConfiguration(search_results_per_page=10,
                                            xds_configuration=xds_config)
            xds_ui_Obj.return_value = xds_ui_Obj
            xds_ui_Obj.first.return_value = xds_ui_cfg

            # create user, save user, login using client
            user = XDSUser.objects.create_user(self.email,
                                               self.password,
                                               first_name=self.first_name,
                                               last_name=self.last_name)
            _, token = AuthToken.objects.create(user)

            response = self.client \
                .get(url, HTTP_AUTHORIZATION='Token {}'.format(token))
            response_dict = json.loads(response.content)

            self.assertEqual(response_dict['search_results_per_page'],
                             xds_ui_cfg.search_results_per_page)
            self.assertEqual(response_dict['search_sort_options'], [])
            self.assertEqual(response_dict['course_highlights'], [])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_spotlight_courses(self):
        """test that calling the endpoint /api/spotlight-courses returns a
            list of documents for configured spotlight courses"""
        url = reverse('xds_api:spotlight-courses')

        with patch('xds_api.views.send_log_email'), \
                patch('xds_api.views.get_request') as get_request, \
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

        with patch('xds_api.views.send_log_email'), \
                patch('xds_api.views.get_request') as get_request, \
                patch('xds_api.views.'
                      'get_spotlight_courses_api_url') as get_api_url:
            get_api_url.return_value = "www.test.com"
            get_request.side_effect = [HTTPError]

            response = self.client.get(url)
            responseDict = json.loads(response.content)

            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(responseDict['message'], errorMsg)

    def test_register_view(self):
        """Test that calling /api/auth/register creates a new user and
            returns the user along with a token"""
        url = reverse('xds_api:register')

        response = self.client.post(url, self.userDict)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(responseDict['token'] is not None)
        self.assertTrue(responseDict['user'] is not None)

    def test_login_view(self):
        """Test that calling /api/auth/login returns a token and user object
            if the credentials are valid"""
        url = reverse('xds_api:login')
        # create user, save user, login using client
        XDSUser.objects.create_user(self.email,
                                    self.password,
                                    first_name=self.first_name,
                                    last_name=self.last_name)

        response = self.client.post(url, self.userDict_login)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(responseDict['token'] is not None)
        self.assertTrue(responseDict['user'] is not None)

    def test_login_view_fail(self):
        """Test that calling /api/auth/login returns an error if the
            credentials are invalid"""
        url = reverse('xds_api:login')

        response = self.client.post(url, self.userDict_login_fail)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_courses(self):
        """Test that calling the endpoint /api/experiences returns a single
            course for the given course ID"""
        doc_id = '123456'
        url = reverse('xds_api:get_courses', args=(doc_id,))

        with patch('xds_api.views.get_request') as get_request:
            http_resp = get_request.return_value
            get_request.return_value = http_resp
            http_resp.json.return_value = [{
                "metadata": {
                    "Metadata_Ledger": {},
                    "Supplemental_Ledger": {}
                },
                "unique_record_identifier": "1234",
                "metadata_key_hash": "5678"
            }]
            http_resp.status_code = 200

            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_courses_error(self):
        """Test that calling the endpoint /api/experiences returns an
            http error if an exception a thrown while reaching out to XIS"""
        doc_id = '123456'
        url = reverse('xds_api:get_courses', args=(doc_id,))
        errorMsg = "error reaching out to configured XIS API; " + \
                   "please check the XIS logs"

        with patch('xds_api.views.get_request') as get_request:
            get_request.side_effect = RequestException

            response = self.client.get(url)
            responseDict = json.loads(response.content)

            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(responseDict['message'], errorMsg)

    def test_get_all_interest_lists_no_auth(self):
        """Test that an unauthenticated user can fetch all interest lists
            through the /api/interest-lists endpoint"""
        url = reverse('xds_api:interest-lists')
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test that we get 2 interest lists (saved in the test setup)
        self.assertEqual(len(responseDict), 3)

    def test_get_all_interest_lists_auth(self):
        """Test that an authenticated user only gets their created interest
            lists when calling the /api/interest-lists api"""
        url = reverse('xds_api:interest-lists')
        _, token = AuthToken.objects.create(self.user_1)
        response = self.client \
            .get(url, HTTP_AUTHORIZATION='Token {}'.format(token))
        responseDict = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict[0]["owner"]["email"], self.user_1.email)

    def test_create_interest_list_no_auth(self):
        """Test that trying to create an interest list through the
            /api/interest-lists api returns an error"""
        url = reverse('xds_api:interest-lists')
        interest_list = {
            "name": "Devops",
            "description": "Devops Desc"
        }
        response = self.client.post(url, interest_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_interest_list_auth(self):
        """Test that trying to create an interest list through the
            /api/interest-lists api succeeds"""
        url = reverse('xds_api:interest-lists')
        interest_list = {
            "name": "Devops",
            "description": "Devops Desc",
            "courses": []
        }
        _, token = AuthToken.objects.create(self.user_1)
        response = \
            self.client.post(url,
                             interest_list,
                             HTTP_AUTHORIZATION='Token {}'.format(token))
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED),
        self.assertEqual(responseDict["name"], "Devops")

    def test_get_interest_by_id_not_found(self):
        """Test that requesting an interest list by ID using the
            /api/interest-lists/id api returns an error if none is found"""
        id = '1234'
        url = reverse('xds_api:interest-list', args=(id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_interest_by_id_no_course(self):
        """Test that requesting an interest list by ID using the
            /api/interest-lists/id api returns an empty array if the list
            contains 0 courses"""
        id = self.list_3.pk
        url = reverse('xds_api:interest-list', args=(id,))
        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(responseDict["experiences"]), 0)
        self.assertEqual(responseDict["name"], self.list_3.name)

    def test_get_interest_by_id_has_course(self):
        """Test that requesting an interest list by ID using the
            /api/interest-lists/id api returns a complete list if the list
            contains courses"""
        id = self.list_1.pk
        url = reverse('xds_api:interest-list', args=(id,))

        with patch('xds_api.views.get_request') as get_request, \
                patch('xds_api.views.XDSConfiguration.objects') as conf_obj:
            conf_obj.return_value = conf_obj
            conf_obj.first.return_value = \
                XDSConfiguration(target_xis_metadata_api="www.test.com")
            http_resp = get_request.return_value
            get_request.return_value = http_resp
            http_resp.json.return_value = [{
                "test": "value",
            }]
            http_resp.status_code = 200
            response = self.client.get(url)
            responseDict = json.loads(response.content)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(responseDict["experiences"], [None])

    def test_get_interest_by_id_no_xis(self):
        """Test that requesting an interest list by ID using the
            /api/interest-lists/id api returns an error if the configured xis
            is unreachable"""
        id = self.list_1.pk
        url = reverse('xds_api:interest-list', args=(id,))

        with patch('xds_api.views.get_request') as get_request, \
                patch('xds_api.views.XDSConfiguration.objects') as conf_obj:
            conf_obj.return_value = conf_obj
            conf_obj.first.return_value = \
                XDSConfiguration(target_xis_metadata_api="www.test.com")
            http_resp = get_request.return_value
            get_request.return_value = http_resp
            http_resp.json.return_value = [{
                "test": "value"
            }]
            http_resp.status_code = 500
            response = self.client.get(url)

            self.assertEqual(response.status_code,
                             status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_edit_interest_list_no_auth(self):
        """Test that unauthenticated users cannot made edits to lists using the
            /api/interest-list/id PATCH"""
        id = self.list_1.pk
        url = reverse('xds_api:interest-list', args=(id,))
        response = self.client.patch(url, data={"test": "test"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_interest_list_not_owner(self):
        """Test that users cannot made edits to lists they do not own using the
            /api/interest-list/id PATCH"""
        id = self.list_2.pk
        url = reverse('xds_api:interest-list', args=(id,))
        _, token = AuthToken.objects.create(self.user_1)
        response = \
            self.client.patch(url,
                              data={"test": "test"},
                              HTTP_AUTHORIZATION='Token {}'.format(token))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_interest_list_success(self):
        """Test that editing an interest list is successful using the \
            /api/interest-list/id PATCH"""
        id = self.list_1.id
        url = reverse('xds_api:interest-list', args=(id,))
        _, token = AuthToken.objects.create(self.user_1)
        new_name = "edited name"
        empty_list = []
        new_list = {"name": new_name,
                    "description": self.list_1.description,
                    "experiences": empty_list}
        response = \
            self.client.patch(url,
                              data=json.dumps(new_list),
                              HTTP_AUTHORIZATION='Token {}'.format(token),
                              content_type="application/json")
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict["name"], new_name)
        self.assertEqual(responseDict["experiences"], [])

    def test_add_course_multiple_lists_no_auth(self):
        """Test that adding a course to multple lists throws an error when\
            user is unauthenticated via /api/add-course-to-lists POST api"""
        id = self.course_1.pk
        url = reverse('xds_api:add_course_to_lists', args=(id,))
        response = self.client.post(url, {"test": "test"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_course_multiple_lists_success(self):
        """Test that adding a course to multiple lists is successful when\
            user is owner for the /api/add-course-to-lists POST api"""
        id = self.course_1.pk
        url = reverse('xds_api:add_course_to_lists', args=(id,))
        _, token = AuthToken.objects.create(self.user_2)
        data = {
            "lists": [self.list_3.pk]
        }
        response = \
            self.client.post(url,
                             data,
                             HTTP_AUTHORIZATION='Token {}'.format(token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.list_3.experiences.all()), 1)

    def test_get_owned_interest_lists_auth(self):
        """Test that an authenticated user only gets their created interest
            lists when calling the /api/interest-lists/owned api"""
        url = reverse('xds_api:owned-lists')
        _, token = AuthToken.objects.create(self.user_1)
        response = self.client \
            .get(url, HTTP_AUTHORIZATION='Token {}'.format(token))
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
        _, token = AuthToken.objects.create(self.user_1)
        # subscribe user 1 to interest list 3
        self.list_3.subscribers.add(self.user_1)
        self.list_3.save()
        response = self.client \
            .get(url, HTTP_AUTHORIZATION='Token {}'.format(token))
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.list_3.subscribers.all()),
                         len(responseDict))

    def test_interest_list_subscribe(self):
        """Test that an authenticated user can subscribe to an interest list
            when calling the endpoint /api/interest-lists/<id>/subscribe"""
        list_id = self.list_2.pk
        url = reverse('xds_api:interest-list-subscribe', args=(list_id,))
        _, token = AuthToken.objects.create(self.user_1)
        response = self.client \
            .patch(url, HTTP_AUTHORIZATION='Token {}'.format(token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.list_2.subscribers.all()), 1)

    def test_interest_list_unsubscribe(self):
        """Test that an authenticated user can unsubscribe to an interest list
            when calling the endpoint /api/interest-lists/<id>/unsubscribe"""
        list_id = self.list_2.pk
        url = reverse('xds_api:interest-list-unsubscribe', args=(list_id,))
        _, token = AuthToken.objects.create(self.user_1)
        # subscribe user 1 to interest list 3
        self.list_2.subscribers.add(self.user_1)
        self.list_2.save()
        response = self.client \
            .patch(url, HTTP_AUTHORIZATION='Token {}'.format(token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.list_2.subscribers.all()), 0)

    def test_create_saved_filters_no_auth(self):
        """Test that trying to create a saved filter through the
            /api/saved-filters api returns an error"""
        url = reverse('xds_api:saved-filters')
        saved_filter = {
            "name": "Devops",
            "query": "randomQuery"
        }
        response = self.client.post(url, saved_filter)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_saved_filters_auth(self):
        """Test that trying to create saved filter through the
            /api/saved-filters api succeeds"""
        url = reverse('xds_api:saved-filters')
        saved_filter = {
            "name": "Devops",
            "query": "randomQuery"
        }
        _, token = AuthToken.objects.create(self.user_1)
        response = \
            self.client.post(url,
                             saved_filter,
                             HTTP_AUTHORIZATION='Token {}'.format(token))
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED),
        self.assertEqual(responseDict["name"], "Devops")

    def test_get_saved_filters(self):
        """Test that trying to get saved filter through the
            /api/saved-filters api succeeds"""
        url = reverse('xds_api:saved-filters')

        saved_config = SavedFilter(owner=self.user_1,
                                   name="Devops", query="randomQuery")
        saved_config.save()

        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict[0]["name"], "Devops")

    def test_get_saved_filter(self):
        """Test that trying to get saved filter through the
            /api/saved-filter api succeeds"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))

        response = self.client.get(url)
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict["name"], "Devops")

    def test_edit_saved_filter_no_auth(self):
        """Test that unauthenticated users cannot made edits to filters
        using the /api/saved-filter/id PATCH"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        response = self.client.patch(url, data={"test": "test"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_saved_filter_not_owner(self):
        """Test that users cannot made edits to filters they do not own
        using the /api/saved-filter/id PATCH"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        _, token = AuthToken.objects.create(self.user_2)
        response = \
            self.client.patch(url,
                              data={"test": "test"},
                              HTTP_AUTHORIZATION='Token {}'.format(token))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_saved_filter_success(self):
        """Test that editing an filter is successful using the \
            /api/saved-filter/id PATCH"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        _, token = AuthToken.objects.create(self.user_1)
        new_name = "edited name"
        new_list = {"name": new_name,
                    "query": self.filter_2.query
                    }
        response = \
            self.client.patch(url,
                              data=json.dumps(new_list),
                              HTTP_AUTHORIZATION='Token {}'.format(token),
                              content_type="application/json")
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(responseDict["name"], new_name)
        self.assertEqual(responseDict["query"], self.filter_2.query)

    def test_delete_saved_filter_no_auth(self):
        """Test that unauthenticated users cannot remove filters
        using the /api/saved-filter/id DELETE"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_saved_filter_not_owner(self):
        """Test that users cannot remove filters they do not own
        using the /api/saved-filter/id DELETE"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        _, token = AuthToken.objects.create(self.user_2)
        response = \
            self.client.delete(url,
                               HTTP_AUTHORIZATION='Token {}'.format(token))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_saved_filter_success(self):
        """Test that removing an filter is successful using the \
            /api/saved-filter/id DELETE"""
        filter_id = self.filter_1.pk
        url = reverse('xds_api:saved-filter', args=(filter_id,))
        _, token = AuthToken.objects.create(self.user_1)

        response = \
            self.client.delete(url,
                               HTTP_AUTHORIZATION='Token {}'.format(token),
                               content_type="application/json")
        responseDict = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(responseDict["message"])
