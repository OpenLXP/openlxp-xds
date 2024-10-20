from rest_framework import serializers
from xds_api.serializers import (CourseDetailHighlightSerializer,
                                 CourseInformationMappingSerializer,
                                 SearchSortOptionSerializer)

from .models import XDSConfiguration, XDSUIConfiguration


# config serializers
class XDSConfigurationSerializer(serializers.ModelSerializer):
    """Serializes the XDSConfiguration Model"""

    class Meta:
        model = XDSConfiguration

        fields = ['target_xis_metadata_api']


class XDSUIConfigurationSerializer(serializers.ModelSerializer):
    """Serializes the XDSUIConfiguration Model"""

    search_sort_options = SearchSortOptionSerializer(many=True, read_only=True)
    course_highlights = CourseDetailHighlightSerializer(many=True,
                                                        read_only=True)
    course_information = CourseInformationMappingSerializer(read_only=True)

    class Meta:
        model = XDSUIConfiguration

        exclude = ('xds_configuration',)
