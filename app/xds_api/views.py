import json
import logging

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseServerError
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from configurations.models import XDSConfiguration
from core.models import CourseSpotlight, Experience, InterestList, SavedFilter
from xds_api.serializers import InterestListSerializer, SavedFilterSerializer
from xds_api.utils.xds_utils import (get_request,
                                     get_spotlight_courses_api_url,
                                     metadata_to_target, save_experiences)

logger = logging.getLogger('dict_config_logger')


class GetSpotlightCoursesView(APIView):
    """Gets Spotlight Courses from XIS"""

    def get(self, request):
        """This method defines an API for fetching configured course
            spotlights from XIS"""

        errorMsg = {
            "message": "error fetching spotlight courses; " +
            "please check the XDS logs"
        }
        errorMsgJSON = json.dumps(errorMsg)

        try:
            if CourseSpotlight.objects.filter(active=True).count() > 0:
                api_url = get_spotlight_courses_api_url()
                logger.info(api_url)
                # make API call
                response = get_request(api_url)
                responseJSON = []
                while response.status_code // 10 == 20:
                    responseJSON += response.json()['results']

                    if 'next' in response.json() and \
                            response.json()['next'] is not None:
                        response = get_request(response.json()['next'])
                    else:
                        break

                if response.status_code == 200:
                    formattedResponse = json.dumps(
                        metadata_to_target(responseJSON))

                    return HttpResponse(formattedResponse,
                                        content_type="application/json")
                else:
                    return HttpResponse(responseJSON,
                                        content_type="application/json")
            else:
                return HttpResponse([])

        except requests.exceptions.RequestException as e:
            errorMsg = {"message": "error reaching out to configured XIS" +
                        " API; please check the XIS logs"}
            errorMsgJSON = json.dumps(errorMsg)
            logger.error(e)
            return HttpResponseServerError(errorMsgJSON,
                                           content_type="application/json")


class GetExperiencesView(APIView):
    """Gets a specific Experience from XIS"""

    def get(self, request, exp_hash):
        """This method defines an API for fetching a single course by ID
            from the XIS"""
        errorMsg = {
            "message": "error fetching course with hash: " + exp_hash +
            "; please check the XDS logs"
        }
        errorMsgJSON = json.dumps(errorMsg)

        try:
            composite_api_url = XDSConfiguration.objects.first() \
                .target_xis_metadata_api
            courseQuery = "?metadata_key_hash_list=" + exp_hash
            api_url = composite_api_url + courseQuery
            logger.info(api_url)
            # make API call
            response = get_request(api_url)
            logger.info(api_url)
            responseJSON = []
            # expected response is a list of 1 element
            if response.status_code//10 == 20:
                responseJSON += response.json()['results']

                if not responseJSON:
                    return Response({"message": "Key not found"},
                                    status.HTTP_404_NOT_FOUND)

                logger.info(responseJSON)
                formattedResponse = json.dumps(
                    metadata_to_target(responseJSON[0]))

                return HttpResponse(formattedResponse,
                                    content_type="application/json")
            else:
                return HttpResponse(response.json()['results'],
                                    content_type="application/json")

        except requests.exceptions.RequestException as e:
            errorMsg = {"message": "error reaching out to configured XIS "
                        + "API; please check the XIS logs"}
            errorMsgJSON = json.dumps(errorMsg)

            logger.error(e)
            return HttpResponseServerError(errorMsgJSON,
                                           content_type="application/json")
        except ObjectDoesNotExist as not_found_err:
            errorMsg = {"message": "No configured XIS URL found"}
            logger.error(not_found_err)
            return Response(errorMsg, status.HTTP_404_NOT_FOUND)

        except KeyError as no_element_err:
            logger.error(no_element_err)
            logger.error(response)
            return Response(errorMsg, status.HTTP_404_NOT_FOUND)


class InterestListsView(APIView):
    """Handles HTTP requests for interest lists"""

    def get(self, request):
        """Retrieves interest lists"""
        errorMsg = {
            "message": "Error fetching records please check the logs."
        }
        # initially fetch all public records not owned by the current user
        querySet = InterestList.objects.filter(
            public=True).exclude(owner=request.user)

        try:
            serializer_class = InterestListSerializer(querySet, many=True)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(err)
            return Response(errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer_class.data, status.HTTP_200_OK)

    def post(self, request):
        """Updates interest lists"""

        # Assign data from request to serializer
        serializer = InterestListSerializer(data=request.data)

        if not serializer.is_valid():
            # If not received send error and bad request status
            logger.info(json.dumps(request.data))
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        # If received save record in ledger and send response of UUID &
        # status created
        serializer.save(owner=request.user)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)


class InterestListView(APIView):
    """Handles HTTP requests for a specific interest list"""
    errorMsg = {
        "message": "error: no record for corresponding interest list id: " +
                   "please check the logs"
    }

    def get(self, request, list_id):
        """This method gets a single interest list"""

        try:
            queryset = InterestList.objects.get(pk=list_id)

            # check if current user can view this list
            if(not(queryset.public or queryset.owner == request.user or
                   request.user in queryset.subscribers.all())):
                return Response({"message": "The current user can not access"
                                 + " this Interest List"},
                                status=status.HTTP_401_UNAUTHORIZED)

            serializer_class = InterestListSerializer(queryset)
            # fetch actual courses for each id in the courses array
            interestList = serializer_class.data
            courseQuery = "?metadata_key_hash_list="
            coursesDict = interestList['experiences']

            # for each hash key in the courses list, append them to the query
            for idx, metadata_key_hash in enumerate(coursesDict):
                if idx == len(coursesDict) - 1:
                    courseQuery += metadata_key_hash
                else:
                    courseQuery += (metadata_key_hash + ",")

            if len(coursesDict) > 0:
                # get search string
                composite_api_url = XDSConfiguration.objects.first() \
                    .target_xis_metadata_api
                api_url = composite_api_url + courseQuery

                # make API call
                response = get_request(api_url)
                responseJSON = []
                while response.status_code//10 == 20:
                    responseJSON += response.json()['results']

                    if 'next' in response.json() and\
                            response.json()['next'] is not None:
                        response = get_request(response.json()['next'])
                    else:
                        break

                if response.status_code == 200:
                    formattedResponse = metadata_to_target(responseJSON)
                    interestList['experiences'] = formattedResponse

                    return Response(interestList,
                                    status=status.HTTP_200_OK)
                else:
                    return Response(response.json(),
                                    status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist as not_found_err:
            logger.error(not_found_err)
            return Response(self.errorMsg, status.HTTP_404_NOT_FOUND)
        except Exception as err:
            logger.error(err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer_class.data, status.HTTP_200_OK)

    def patch(self, request, list_id):
        """This method updates a single interest list"""

        try:
            queryset = InterestList.objects.get(pk=list_id)

            # check user is owner of list
            if not request.user == queryset.owner:
                return Response({'Current user does not have access to '
                                'modify the list'},
                                status.HTTP_401_UNAUTHORIZED)
            # save new experiences
            save_experiences(request.data['experiences'])
            # Assign data from request to serializer
            serializer = InterestListSerializer(queryset, data=request.data)

            if not serializer.is_valid():
                # If not received send error and bad request status
                logger.info(json.dumps(request.data))
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

            serializer.save(owner=request.user)

            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist as not_found_err:
            logger.error(not_found_err)
            return Response(self.errorMsg, status.HTTP_404_NOT_FOUND)
        except Exception as err:
            logger.error(err)
            return Response(err, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, list_id):
        """This method deletes a single interest list"""

        try:
            queryset = InterestList.objects.get(pk=list_id)

            # check user is owner of list
            if not request.user == queryset.owner:
                return Response({'Current user does not have access to '
                                'delete the list'},
                                status.HTTP_401_UNAUTHORIZED)
            # delete list
            queryset = InterestList.objects.get(pk=list_id)
            queryset.delete()

            return Response({"message": "List successfully deleted!"},
                            status=status.HTTP_200_OK)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist as not_found_err:
            logger.error(not_found_err)
            return Response(self.errorMsg, status.HTTP_404_NOT_FOUND)
        except Exception as err:
            logger.error(err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddCourseToListsView(APIView):
    """Add courses to multiple interest lists"""

    def post(self, request, exp_hash):
        """This method handles request for adding a single course to multiple
            interest lists at once"""
        errorMsg = {
            "message": "error: unable to add course to provided "
            + "interest lists."
        }

        try:
            # get user
            user = request.user

            # get or add course
            course, created = \
                Experience.objects.get_or_create(pk=exp_hash)
            data = request.data['lists']
            if not isinstance(data, list):
                data = [data]
            course.save()
            # check user is onwer of lists
            for list_id in data:
                currList = InterestList.objects.get(pk=list_id)

                if user == currList.owner:
                    currList.experiences.add(course)
                    currList.save()
            # add course to each list
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": "course successfully added!"},
                            status.HTTP_200_OK)


class InterestListsOwnedView(APIView):
    """Gets interest lists owned by the current user"""

    def get(self, request):
        """Handles HTTP requests for interest lists managed by request user"""
        errorMsg = {
            "message": "Error fetching records please check the logs."
        }
        # get user
        user = request.user

        try:
            querySet = InterestList.objects.filter(owner=user)
            serializer_class = InterestListSerializer(querySet, many=True)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer_class.data, status.HTTP_200_OK)


class InterestListsSubscriptionsView(APIView):
    """Gets interest lists the current user follows"""

    def get(self, request):
        """Handles HTTP requests for interest lists that the request user is
            subscribed to"""
        errorMsg = {
            "message": "Error fetching records please check the logs."
        }
        # get user
        user = request.user

        try:
            querySet = user.subscriptions
            serializer_class = InterestListSerializer(querySet, many=True)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer_class.data, status.HTTP_200_OK)


class InterestListSubscribeView(APIView):
    """Subscribes current user to a specific interest list"""

    def patch(self, request, list_id):
        """
        This method handles a request for subscribing to an interest list
        """
        errorMsg = {
            "message": "error: unable to subscribe user to list: "
            + str(list_id)
        }

        try:
            # get user
            user = request.user

            # get interest list
            interest_list = InterestList.objects.get(pk=list_id, public=True)
            interest_list.subscribers.add(user)
            interest_list.save()
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": "user successfully subscribed to "
                             + "list!"},
                            status.HTTP_200_OK)


class InterestListUnsubscribeView(APIView):
    """Removes a user from subscribing to a specific interest list"""

    def patch(self, request, list_id):
        """
        This method handles a request for unsubscribing from an interest list
        """
        errorMsg = {
            "message": "error: unable to unsubscribe user from list: " +
            str(list_id)
        }

        try:
            # get user
            user = request.user

            # get interest list
            interest_list = InterestList.objects.get(pk=list_id)
            interest_list.subscribers.remove(user)
            interest_list.save()
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return \
                Response({"message": "user successfully unsubscribed "
                          + "from list!"},
                         status.HTTP_200_OK)


class SavedFiltersOwnedView(APIView):
    """Returns filters saved by the current user"""

    def get(self, request):
        """
        Handles HTTP requests for saved filters managed by request user
        """
        errorMsg = {
            "message": "Error fetching records please check the logs."
        }
        # get user
        user = request.user

        try:
            querySet = SavedFilter.objects.filter(owner=user)
            serializer_class = SavedFilterSerializer(querySet, many=True)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer_class.data, status.HTTP_200_OK)


class SavedFilterView(APIView):
    """Handles HTTP requests for a specific saved filter"""
    errorMsg = {
        "message": "error: no record for corresponding saved filter id: " +
                   "please check the logs"
    }

    def get(self, request, filter_id):
        """Retrieve a specific saved filter"""

        try:
            queryset = SavedFilter.objects.get(pk=filter_id)

            serializer_class = SavedFilterSerializer(queryset)

            return Response(serializer_class.data, status.HTTP_200_OK)

        except HTTPError as http_err:
            logger.error(http_err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist as not_found_err:
            logger.error(not_found_err)
            return Response(self.errorMsg, status.HTTP_404_NOT_FOUND)
        except Exception as err:
            logger.error(err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, filter_id):
        """Update a specific saved filter"""

        try:
            queryset = SavedFilter.objects.get(pk=filter_id)

            # check user is owner of filter
            if not request.user == queryset.owner:
                return Response({'Current user does not have access to '
                                 'modify the saved filter'},
                                status.HTTP_401_UNAUTHORIZED)
            # Assign data from request to serializer
            serializer = SavedFilterSerializer(queryset, data=request.data)

            if not serializer.is_valid():
                # If not received send error and bad request status
                logger.info(json.dumps(request.data))
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist as not_found_err:
            logger.error(not_found_err)
            return Response(self.errorMsg, status.HTTP_404_NOT_FOUND)
        except Exception as err:
            logger.error(err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, filter_id):
        """Delete a specific saved filter"""

        try:
            queryset = SavedFilter.objects.get(pk=filter_id)

            # check user is owner of list
            if not request.user == queryset.owner:
                return Response({'Current user does not have access to '
                                 'delete the saved filter'},
                                status.HTTP_401_UNAUTHORIZED)
            # delete filter
            queryset = SavedFilter.objects.get(pk=filter_id)
            queryset.delete()

            return Response({"message": "Filter successfully deleted!"},
                            status=status.HTTP_200_OK)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist as not_found_err:
            logger.error(not_found_err)
            return Response(self.errorMsg, status.HTTP_404_NOT_FOUND)
        except Exception as err:
            logger.error(err)
            return Response(self.errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)


class SavedFiltersView(APIView):
    """Handles HTTP requests for multiple saved filters"""

    def get(self, request):
        """Gets saved filters"""

        errorMsg = {
            "message": "Error fetching records please check the logs."
        }
        # initially fetch all saved filters
        querySet = SavedFilter.objects.all()

        try:
            serializer_class = SavedFilterSerializer(querySet, many=True)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(err)
            return Response(errorMsg,
                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer_class.data, status.HTTP_200_OK)

    def post(self, request):
        """Update saved filters"""

        # Assign data from request to serializer
        serializer = SavedFilterSerializer(data=request.data)

        if not serializer.is_valid():
            # If not received send error and bad request status
            logger.info(json.dumps(request.data))
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.save(owner=request.user)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)
