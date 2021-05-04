import json
import logging

import requests
from django.http import HttpResponse, HttpResponseServerError
from requests.exceptions import HTTPError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import XDSConfiguration, XDSUIConfiguration
from xds_api.serializers import (XDSConfigurationSerializer,
                                 XDSUIConfigurationSerializer)
from xds_api.utils.xds_utils import (get_request,
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

    def get(self, request):
        """Returns the XDSUI configuration fields from the model"""
        ui_config = XDSUIConfiguration.objects.first()
        serializer = XDSUIConfigurationSerializer(ui_config)

        return Response(serializer.data)
