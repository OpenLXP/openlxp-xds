from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import XDSUser


# user serializer
class XDSUserSerializer(serializers.ModelSerializer):
    """Serializes the XDSUser model"""

    class Meta:
        model = XDSUser
        fields = ('id', 'email', 'first_name', 'last_name')


# register serializer
class RegisterSerializer(serializers.ModelSerializer):
    """Serializes the registration form from the API"""

    class Meta:
        model = XDSUser
        fields = ('id', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Create a user"""
        user = XDSUser.objects \
            .create_user(validated_data['email'],
                         validated_data['password'],
                         first_name=validated_data['first_name'],
                         last_name=validated_data['last_name'])

        return user


# login serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """Validate a user is active in the system"""

        # the user object
        user = authenticate(**data)

        if user and user.is_active:
            return user

        # returns when user is inactive or not in the system
        raise serializers.ValidationError('Incorrect Credentials')
