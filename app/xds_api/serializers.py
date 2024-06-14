import logging

from rest_framework import serializers

from configurations.models import CourseInformationMapping
from core.models import (CourseDetailHighlight, Experience, InterestList,
                         SavedFilter, SearchSortOption)
from users.serializers import XDSUserSerializer

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
                  'xds_ui_configuration', 'highlight_icon', ]


class CourseInformationMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInformationMapping
        exclude = ['xds_ui_configuration']


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializes the Course model"""

    class Meta:
        model = Experience
        fields = ['metadata_key_hash']


class InterestListSerializer(serializers.ModelSerializer):
    """Serializes the interest list model"""
    owner = XDSUserSerializer(read_only=True)
    subscribers = XDSUserSerializer(many=True, read_only=True)

    class Meta:
        model = InterestList
        fields = '__all__'

    def create(self, validated_data):
        name = validated_data.get("name")
        description = validated_data.get("description")
        owner = validated_data.get("owner")
        public = validated_data.get("public", False)
        return InterestList.objects.create(name=name,
                                           description=description,
                                           owner=owner,
                                           public=public)

    def update(self, instance, validated_data):
        instance.owner = validated_data.get('owner', instance.owner)
        instance.description = validated_data.get('description',
                                                  instance.description)
        instance.name = validated_data.get('name', instance.name)
        instance.public = validated_data.get('public', instance.public)
        experiences = validated_data.get('experiences')
        # for each experience in the experience list, we add the experience to
        # the current interest list
        course_added_count = 0
        for course in experiences:
            if course not in instance.experiences.all():
                instance.experiences.add(course)
                course_added_count += 1

        # for each saved experience in the experience list, we remove the
        # experience if we don't find it in the passed in the updated list
        for exp in instance.experiences.all():
            if exp not in experiences:
                instance.experiences.remove(exp)

        #  writing content to file
        # msg = ("Count of New Courses added: " + str(course_added_count))

        list_subscribers = []
        for each_subscriber in instance.subscribers.all():
            list_subscribers.append(each_subscriber.email)

        instance.save()
        return instance


class SavedFilterSerializer(serializers.ModelSerializer):
    """Serializes the Saved filter model"""
    owner = XDSUserSerializer(read_only=True)

    class Meta:
        model = SavedFilter
        fields = '__all__'

    def create(self, validated_data):
        return SavedFilter.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.owner = validated_data.get('owner', instance.owner)
        instance.name = validated_data.get('name', instance.name)
        instance.query = validated_data.get('query', instance.query)
        instance.save()

        return instance
