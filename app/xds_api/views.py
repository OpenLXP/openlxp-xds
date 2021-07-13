import json
import logging

import requests
from django.http import HttpResponse, HttpResponseServerError
from knox.models import AuthToken
from requests.exceptions import HTTPError
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from core.management.utils.xds_internal import send_log_email
from core.models import XDSConfiguration, XDSUIConfiguration
from xds_api.serializers import (LoginSerializer, RegisterSerializer,
                                 XDSConfigurationSerializer,
                                 XDSUIConfigurationSerializer,
                                 XDSUserSerializer)
from xds_api.utils.xds_utils import (get_courses_api_url, get_request,
                                     get_spotlight_courses_api_url,
                                     metadata_to_target)

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
            formattedResponse = metadata_to_target(responseJSON)

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
            formattedResponse = metadata_to_target(responseJSON)

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
