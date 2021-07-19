import json
import logging

import requests
from django.http import HttpResponse, HttpResponseServerError
from knox.models import AuthToken
from requests.exceptions import HTTPError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes

from core.management.utils.xds_internal import send_log_email
from core.models import InterestList, XDSConfiguration, XDSUIConfiguration
from xds_api.serializers import (InterestListSerializer, LoginSerializer,
                                 RegisterSerializer,
                                 XDSConfigurationSerializer,
                                 XDSUIConfigurationSerializer,
                                 XDSUserSerializer)
from xds_api.utils.xds_utils import (get_courses_api_url, get_request,
                                     get_spotlight_courses_api_url,
                                     metadata_to_target, save_courses)

logger = logging.getLogger('dict_config_logger')


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
        send_log_email(errorMsgJSON)
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


def get_courses(request, course_id):
    """This method defines an API for fetching a single course by ID
        from the XIS"""
    errorMsg = {
        "message": "error fetching course with ID " + course_id + "; " +
        "please check the XDS logs"
    }
    errorMsgJSON = json.dumps(errorMsg)

    try:
        api_url = get_courses_api_url(course_id)

        # make API call
        response = get_request(api_url)
        logger.info(api_url)
        responseJSON = json.dumps(response.json())
        logger.info(responseJSON)

        if (response.status_code == 200):
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


class XDSConfigurationView(APIView):
    """XDS Configuration View"""

    def get(self, request):
        """Returns the configuration fields from the model"""
        config = XDSConfiguration.objects.first()
        serializer = XDSConfigurationSerializer(config)

        return Response(serializer.data)


class XDSUIConfigurationView(APIView):
    """XDSUI Condiguration View"""
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        """Returns the XDSUI configuration fields from the model"""
        ui_config = XDSUIConfiguration.objects.first()
        serializer = XDSUIConfigurationSerializer(ui_config)

        return Response(serializer.data)


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
        })


@api_view(['GET', 'POST'])
def interest_lists(request):
    """Handles HTTP requests for interest lists"""
    if request.method == 'GET':
        errorMsg = {
            "message": "Error fetching records please check the logs."
        }
        # initially fetch all active records
        user = request.user
        querySet = InterestList.objects.all()

        if request.user.is_authenticated:
            querySet = querySet.filter(owner=user)

        try:
            serializer_class = InterestListSerializer(querySet, many=True)
        except HTTPError as http_err:
            logger.error(http_err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(err)
            return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer_class.data, status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Assign data from request to serializer
        user = request.user
        if not request.user.is_authenticated:
            return Response({'Please login to create Interest List'}, 
                            status.HTTP_401_UNAUTHORIZED)

        serializer = InterestListSerializer(data=request.data)
        logger.info("Assigned to serializer")

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


@api_view(['GET', 'PATCH'])
def single_interest_list(request, list_id):
    """This method defines an API to handle requests for a single interest
        list"""
    errorMsg = {
        "message": "error: no record for corresponding interest list id; " +
                   "please check the logs"
    }

    try:
        queryset = InterestList.objects.get(pk=list_id)

        if request.method == 'GET':
            serializer_class = InterestListSerializer(queryset)
            # fetch actual courses for each id in the courses array
            interestList = serializer_class.data
            courseQuery = "?metadata_key_hash="
            coursesDict = interestList['courses']

            for idx, metadata_key_hash in enumerate(coursesDict):
                if idx == len(coursesDict) - 1:
                    courseQuery += metadata_key_hash
                else:
                    courseQuery += (metadata_key_hash + ",")
            
            if (len(coursesDict) > 0):
                # get search string
                composite_api_url = XDSConfiguration.objects.first()\
                    .target_xis_metadata_api
                api_url =composite_api_url + courseQuery

                # make API call
                response = get_request(api_url)
                logger.info(api_url)
                responseJSON = json.dumps(response.json())
                logger.info(responseJSON)

                if (response.status_code == 200):
                    formattedResponse = metadata_to_target(responseJSON)
                    interestList['courses'] = formattedResponse

                    return Response(interestList,
                                    status=status.HTTP_200_OK)
                else:
                    return Response(response.json(),
                                    status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            # Assign data from request to serializer
            user = request.user

            # check user is logged in
            if not request.user.is_authenticated:
                return Response({'Please login to update Interest List'}, 
                                status.HTTP_401_UNAUTHORIZED)

            # check user is owner of list
            if not request.user == queryset.owner:
                return Response({'Current user does not have access to modify '
                                 'the list'}, 
                                status.HTTP_401_UNAUTHORIZED)    
            # save new courses
            save_courses(request.data['courses'])
            serializer = InterestListSerializer(queryset, data=request.data)
            logger.info("Assigned to serializer")

            if not serializer.is_valid():
                # If not received send error and bad request status
                logger.info(json.dumps(request.data))
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

            serializer.save(owner=user)

            return Response(serializer.data,
                            status=status.HTTP_200_OK)
    except HTTPError as http_err:
        logger.error(http_err)
        return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as err:
        logger.error(err)
        return Response(errorMsg, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer_class.data, status.HTTP_200_OK)
