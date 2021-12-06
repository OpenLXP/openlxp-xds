import json
import logging
from openlxp_authentication.serializers import SAMLConfigurationSerializer

import requests
from core.models import (Experience, InterestList, SavedFilter,
                         XDSConfiguration, XDSUIConfiguration)
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseServerError
from knox.models import AuthToken
from openlxp_authentication.models import SAMLConfiguration
from requests.exceptions import HTTPError
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.utils import load_strategy

from xds_api.serializers import (InterestListSerializer, LoginSerializer,
                                 RegisterSerializer, SavedFilterSerializer,
                                 XDSConfigurationSerializer,
                                 XDSUIConfigurationSerializer,
                                 XDSUserSerializer)
from xds_api.utils.xds_utils import (get_request,
                                     get_spotlight_courses_api_url,
                                     handle_unauthenticated_user,
                                     metadata_to_target, save_experiences)

logger = logging.getLogger('dict_config_logger')


@api_view(['GET'])
def get_spotlight_courses(request):
    """This method defines an API for fetching configured course spotlights
        from XIS"""

    errorMsg = {
        "message": "error fetching spotlight courses; " +
                   "please check the XDS logs"
    }
    errorMsgJSON = json.dumps(errorMsg)

    try:
        api_url = get_spotlight_courses_api_url()
        logger.info(api_url)
        # make API call
        response = get_request(api_url)
        responseJSON = json.dumps(response.json())

        if response.status_code == 200:
            formattedResponse = json.dumps(metadata_to_target(responseJSON))

            return HttpResponse(formattedResponse,
                                content_type="application/json")
        else:
            return HttpResponse(responseJSON,
                                content_type="application/json")

    except requests.exceptions.RequestException as e:
        errorMsg = {"message": "error reaching out to configured XIS API; " +
                               "please check the XIS logs"}
        errorMsgJSON = json.dumps(errorMsg)
        logger.error(e)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")

    except HTTPError as http_err:
        logger.error(http_err)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")
    except Exception as err:
        logger.error(err)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")


@api_view(['GET'])
def get_experiences(request, exp_hash):
    """This method defines an API for fetching a single course by ID
        from the XIS"""
    errorMsg = {
        "message": "error fetching course with hash: " + exp_hash + "; " +
                   "please check the XDS logs"
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
        # expected response is a list of 1 element
        responseDict = response.json()
        responseJSON = json.dumps(responseDict[0])
        logger.info(responseJSON)

        if response.status_code == 200:
            formattedResponse = json.dumps(metadata_to_target(responseJSON))

            return HttpResponse(formattedResponse,
                                content_type="application/json")
        else:
            return HttpResponse(responseJSON,
                                content_type="application/json")

    except requests.exceptions.RequestException as e:
        errorMsg = {"message": "error reaching out to configured XIS API; " +
                               "please check the XIS logs"}
        errorMsgJSON = json.dumps(errorMsg)

        logger.error(e)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")
    except ObjectDoesNotExist as not_found_err:
        errorMsg = {"message": "No configured XIS URL found"}
        logger.error(not_found_err)
        return Response(errorMsg, status.HTTP_404_NOT_FOUND)
    except HTTPError as http_err:
        logger.error(http_err)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")
    except Exception as err:
        logger.error(err)
        return HttpResponseServerError(errorMsgJSON,
                                       content_type="application/json")


class XDSConfigurationView(APIView):
    """XDS Configuration View"""

    def get(self, request):
        """Returns the configuration fields from the model"""
        config = XDSConfiguration.objects.first()
        serializer = XDSConfigurationSerializer(config)

        return Response(serializer.data)


class XDSUIConfigurationView(APIView):
    """XDSUI Configuration View"""

    def get(self, request):
        """Returns the XDSUI configuration fields from the model"""
        ui_config = XDSUIConfiguration.objects.first()
        serializer = XDSUIConfigurationSerializer(ui_config)

        login_path = load_strategy(request).build_absolute_uri('/')[:-1]

        serialized_ssos = [{"path": login_path + conf['endpoint'], "name": conf['name']}
                               for conf in SAMLConfigurationSerializer(SAMLConfiguration.objects.all(), many=True).data]

        return Response(dict(**serializer.data, **{"single_sign_on_options": serialized_ssos}))


class RegisterView(generics.GenericAPIView):
    """User Registration API"""

    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        """POST request that takes in: email, password, first_name, and
            last_name"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # creates a token for immediate login
        _, token = AuthToken.objects.create(user)

        # Returning the user context, and token
        return Response({
            "user": XDSUserSerializer(user,
                                      context=self.get_serializer_context()
                                      ).data,
            "token": token
        }, headers={
            "Authorization": f"Token {token}"
        })


class LoginView(generics.GenericAPIView):
    """Logs user in and returns token"""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        # Getting the user token
        _, token = AuthToken.objects.create(user)

        return Response({
            "user": XDSUserSerializer(user,
                                      context=self.get_serializer_context()
                                      ).data,
            "token": token
        }, headers={
            "Authorization": f"Token {token}"
        })


@api_view(['GET', 'POST'])
def interest_lists(request):
    """Handles HTTP requests for interest lists"""

    if request.method == 'GET':
        errorMsg = {
            "message": "Error fetching records please check the logs."
        }
        # initially fetch all active records
        querySet = InterestList.objects.all()

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

    elif request.method == 'POST':
        user = request.user

        if not user.is_authenticated:
            return handle_unauthenticated_user()

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


@api_view(['GET', 'PATCH', 'DELETE'])
def interest_list(request, list_id):
    """This method defines an API to handle requests for a single interest
        list"""
    errorMsg = {
        "message": "error: no record for corresponding interest list id: " +
                   "please check the logs"
    }

    try:
        queryset = InterestList.objects.get(pk=list_id)

        if request.method == 'GET':
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
                responseJSON = json.dumps(response.json())

                if response.status_code == 200:
                    formattedResponse = metadata_to_target(responseJSON)
                    interestList['experiences'] = formattedResponse

                    return Response(interestList,
                                    status=status.HTTP_200_OK)
                else:
                    return Response(response.json(),
                                    status=status.HTTP_503_SERVICE_UNAVAILABLE)
        elif request.method == 'PATCH':
            user = request.user

            # check user is logged in
            if not user.is_authenticated:
                return handle_unauthenticated_user()

            # check user is owner of list
            if not request.user == queryset.owner:
                return Response({'Current user does not have access to modify '
                                 'the list'},
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

            serializer.save(owner=user)

            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            # Assign data from request to serializer
            user = request.user

            # check user is logged in
            if not user.is_authenticated:
                return handle_unauthenticated_user()

            # check user is owner of list
            if not request.user == queryset.owner:
                return Response({'Current user does not have access to delete '
                                 'the list'},
                                status.HTTP_401_UNAUTHORIZED)
            # delete list
            queryset = InterestList.objects.get(pk=list_id)
            queryset.delete()

            return Response({"message": "List successfully deleted!"},
                            status=status.HTTP_200_OK)
    except HTTPError as http_err:
        logger.error(http_err)
        return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
    except ObjectDoesNotExist as not_found_err:
        logger.error(not_found_err)
        return Response(errorMsg, status.HTTP_404_NOT_FOUND)
    except Exception as err:
        logger.error(err)
        return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer_class.data, status.HTTP_200_OK)


@api_view(['POST'])
def add_course_to_lists(request, exp_hash):
    """This method handles request for adding a single course to multiple
        interest lists at once"""
    errorMsg = {
        "message": "error: unable to add course to provided interest lists."
    }

    try:
        # check user is authenticated
        user = request.user

        if not user.is_authenticated:
            return handle_unauthenticated_user()

        # get or add course
        course, created = \
            Experience.objects.get_or_create(pk=exp_hash)
        course.save()
        # check user is onwer of lists
        for list_id in request.data['lists']:
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


@api_view(['GET'])
def interest_lists_owned(request):
    """Handles HTTP requests for interest lists managed by request user"""
    errorMsg = {
        "message": "Error fetching records please check the logs."
    }
    # check user is authenticated
    user = request.user

    if not user.is_authenticated:
        return handle_unauthenticated_user()

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


@api_view(['GET'])
def interest_lists_subscriptions(request):
    """Handles HTTP requests for interest lists that the request user is
        subscribed to"""
    errorMsg = {
        "message": "Error fetching records please check the logs."
    }
    # check user is authenticated
    user = request.user

    if not user.is_authenticated:
        return handle_unauthenticated_user()

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


@api_view(['PATCH'])
def interest_list_subscribe(request, list_id):
    """This method handles a request for subscribing to an interest list"""
    errorMsg = {
        "message": "error: unable to subscribe user to list: " + str(list_id)
    }

    try:
        # check user is authenticated
        user = request.user

        if not user.is_authenticated:
            return handle_unauthenticated_user()

        # get interest list
        interest_list = InterestList.objects.get(pk=list_id)
        interest_list.subscribers.add(user)
        interest_list.save()
    except HTTPError as http_err:
        logger.error(http_err)
        return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as err:
        logger.error(err)
        return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"message": "user successfully subscribed to list!"},
                        status.HTTP_200_OK)


@api_view(['PATCH'])
def interest_list_unsubscribe(request, list_id):
    """This method handles a request for unsubscribing from an interest list"""
    errorMsg = {
        "message": "error: unable to unsubscribe user from list: " +
                   str(list_id)
    }

    try:
        # check user is authenticated
        user = request.user

        if not user.is_authenticated:
            return handle_unauthenticated_user()

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
        return Response({"message":
                         "user successfully unsubscribed from list!"},
                        status.HTTP_200_OK)


@api_view(['GET'])
def saved_filters_owned(request):
    """Handles HTTP requests for saved filters managed by request user"""
    errorMsg = {
        "message": "Error fetching records please check the logs."
    }
    # check user is authenticated
    user = request.user

    if not user.is_authenticated:
        return handle_unauthenticated_user()

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


@api_view(['GET', 'PATCH', 'DELETE'])
def saved_filter(request, filter_id):
    """This method defines an API to handle requests for a single interest
        list"""
    errorMsg = {
        "message": "error: no record for corresponding saved filter id: " +
                   "please check the logs"
    }

    try:
        queryset = SavedFilter.objects.get(pk=filter_id)

        if request.method == 'GET':
            serializer_class = SavedFilterSerializer(queryset)

            return Response(serializer_class.data, status.HTTP_200_OK)
        elif request.method == 'PATCH':
            user = request.user

            # check user is logged in
            if not user.is_authenticated:
                return handle_unauthenticated_user()

            # check user is owner of list
            if not request.user == queryset.owner:
                return Response({'Current user does not have access to modify '
                                 'the saved filter'},
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
        elif request.method == 'DELETE':
            # Assign data from request to serializer
            user = request.user

            # check user is logged in
            if not user.is_authenticated:
                return handle_unauthenticated_user()

            # check user is owner of list
            if not request.user == queryset.owner:
                return Response({'Current user does not have access to delete '
                                 'the saved filter'},
                                status.HTTP_401_UNAUTHORIZED)
            # delete filter
            queryset = SavedFilter.objects.get(pk=filter_id)
            queryset.delete()

            return Response({"message": "Filter successfully deleted!"},
                            status=status.HTTP_200_OK)
    except HTTPError as http_err:
        logger.error(http_err)
        return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
    except ObjectDoesNotExist as not_found_err:
        logger.error(not_found_err)
        return Response(errorMsg, status.HTTP_404_NOT_FOUND)
    except Exception as err:
        logger.error(err)
        return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def saved_filters(request):
    """Handles HTTP requests for saved filters"""
    if request.method == 'GET':
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

    elif request.method == 'POST':
        user = request.user

        if not user.is_authenticated:
            return handle_unauthenticated_user()

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
