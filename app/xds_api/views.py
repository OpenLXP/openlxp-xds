import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import XDSConfiguration
from xds_api.serializers import XDSConfigurationSerializer

logger = logging.getLogger('dict_config_logger')


class XDSConfigurationView(APIView):
    """XDS Configuration View"""

    def get(self, request):
        """Returns the configuration fields from the model"""
        config = XDSConfiguration.objects.first()
        serializer = XDSConfigurationSerializer(config)

        return Response(serializer.data)
