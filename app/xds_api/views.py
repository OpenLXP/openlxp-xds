import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import XDSConfiguration, XDSUIConfiguration
from xds_api.serializers import XDSConfigurationSerializer, \
                                XDSUIConfigurationSerializer

logger = logging.getLogger('dict_config_logger')


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
