from openlxp_authentication.models import SAMLConfiguration
from openlxp_authentication.serializers import SAMLConfigurationSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.utils import load_strategy

from .models import XDSConfiguration, XDSUIConfiguration
from .serializers import (XDSConfigurationSerializer,
                          XDSUIConfigurationSerializer)


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

        serialized_ssos = [
            {"path": login_path + conf['endpoint'], "name": conf['name']}
            for conf in
            SAMLConfigurationSerializer(SAMLConfiguration.
                                        objects.all(), many=True
                                        ).data]

        return Response({**serializer.data,
                         **{"single_sign_on_options": serialized_ssos}})
