import re

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _
from model_utils.models import TimeStampedModel
from rest_framework import exceptions
from rest_framework.permissions import DjangoModelPermissions


class Organization(TimeStampedModel):
    """Model to store an organization for filtering"""
    name = models.CharField(max_length=200, unique=True,
                            null=False, blank=False)
    filter = models.CharField(
        max_length=200, unique=True, null=False, blank=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.filter


class XDSUserProfileManager(BaseUserManager):
    """User manager"""

    def create_user(self, email, password=None, **other_fields):
        """Create a new user"""
        if not email:
            raise ValueError('Email is required')

        # if not first_name:
        #     raise ValueError('First name is required')

        # if not last_name:
        #     raise ValueError('Last name is required')

        email = email.lower()
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **other_fields):
        """Create a super user"""

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        user = self.create_user(email, password, **other_fields)
        return user


class XDSUser(AbstractBaseUser, PermissionsMixin):
    """Model for a user"""

    # User attributes
    username = None
    email = models.EmailField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    date_joined = models.DateTimeField(default=timezone.now)
    organizations = models.ManyToManyField(Organization, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = XDSUserProfileManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        return super(XDSUser, self).save(*args, **kwargs)


class PermissionsChecker(DjangoModelPermissions):
    """
    Class to define the method for checking permissions for the XDS API
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        # if current request is in OPEN_ENDPOINTS doesn't check permissions,
        # returns true
        open_endpoints_regex = '(?:% s)' % '|'.join(
            getattr(settings, 'OPEN_ENDPOINTS', []))
        if re.fullmatch(open_endpoints_regex, request.path_info):
            return True

        # checks if there is a logged in user
        if not request.user or (
                not request.user.is_authenticated and
                self.authenticated_users_only):
            return False

        try:
            # tries to get app and model names from view
            model_meta = self._queryset(view).model._meta

        except Exception:
            # if unable, generates app and model names
            def model_meta():
                return None

            model_meta.app_label = view.__module__.split('.')[0]
            model_meta.model_name = \
                view.get_view_name().lower().replace(' ', '')

        # determines permission required to access this endpoint
        perms = self.get_required_permissions(request.method, model_meta)

        # checks if the user has the required permission
        return request.user.has_perms(perms)

    def get_required_permissions(self, method, model_meta):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_meta.app_label,
            'model_name': model_meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]


class NumberValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\\d', password):
            raise ValidationError(
                _("The password must contain at least 1 digit, 0-9."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 digit, 0-9."
        )


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _(
                    "The password must contain at least 1 uppercase letter, "
                    "A-Z."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase letter, A-Z."
        )


class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _(
                    "The password must contain at least 1 lowercase letter, "
                    "a-z."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 lowercase letter, a-z."
        )


class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\\]{}|\\\\`~!@#$%^&*_\\-+=;:\'",<>./?]',
                          password):
            raise ValidationError(
                _("The password must contain at least 1 symbol: " +
                  "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?"),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 symbol: " +
            "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?"
        )
