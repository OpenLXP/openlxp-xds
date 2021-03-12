from django.shortcuts import render
import logging

from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from xds_api.serializers import XDSConfigurationSerializer
from core.models import XDSConfiguration


logger = logging.getLogger('dict_config_logger')

class XDSConfigurationView(APIView):
    """XDS Configuration View"""

    def get(self, request):
        """Returns the configuration fields from the model"""
        config = XDSConfiguration.objects.first()
        serializer = XDSConfigurationSerializer(config)

        return Response(serializer.data)
