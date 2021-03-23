import logging

from rest_framework import serializers

from core.models import XDSConfiguration

logger = logging.getLogger('dict_config_logger')


class XDSConfigurationSerializer(serializers.ModelSerializer):
    """Serializes the XDSConfiguration Model"""

    class Meta:
        model = XDSConfiguration

        fields = ['target_xis_es_api',
                  'target_xis_metadata_api']
