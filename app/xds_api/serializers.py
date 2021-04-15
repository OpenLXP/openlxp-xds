import logging

from rest_framework import serializers

from core.models import SearchSortOption, XDSConfiguration, \
                        XDSUIConfiguration, CourseDetailHighlight

logger = logging.getLogger('dict_config_logger')


class FilteredListSerializer(serializers.ListSerializer):
    """Extends the ListSerializer to enable us to filter \
        out data before serializing"""

    def to_representation(self, data):
        data = data.filter(active=True)
        return super(FilteredListSerializer, self).to_representation(data)


class OrderedListSerializer(serializers.ListSerializer):
    """Extends the ListSerializer to enable us to filter \
        out data and sort it before serializing"""

    def to_representation(self, data):
        data = data.filter(active=True).order_by('rank')
        return super(OrderedListSerializer, self).to_representation(data)


class XDSConfigurationSerializer(serializers.ModelSerializer):
    """Serializes the XDSConfiguration Model"""

    class Meta:
        model = XDSConfiguration

        fields = ['target_xis_metadata_api']


class SearchSortOptionSerializer(serializers.ModelSerializer):
    """Serializes the SearchSortOption Model"""

    class Meta:
        list_serializer_class = FilteredListSerializer
        model = SearchSortOption

        fields = ['display_name', 'field_name', 'active',
                  'xds_ui_configuration']


class CourseDetailHighlightSerializer(serializers.ModelSerializer):
    """Serializes the CourseDetailHighlight Model"""

    class Meta:
        list_serializer_class = OrderedListSerializer
        model = CourseDetailHighlight

        fields = ['display_name', 'field_name', 'active',
                  'xds_ui_configuration', 'highlight_icon',]


class XDSUIConfigurationSerializer(serializers.ModelSerializer):
    """Serializes the XDSUIConfiguration Model"""

    search_sort_options = SearchSortOptionSerializer(many=True, read_only=True)
    course_highlights = CourseDetailHighlightSerializer(many=True,
                                                        read_only=True)

    class Meta:
        model = XDSUIConfiguration

        exclude = ('xds_configuration',)
