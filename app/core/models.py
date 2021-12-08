import re

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel
from openlxp_notifications.management.utils.notification import \
    email_verification
from rest_framework import exceptions
from rest_framework.permissions import DjangoModelPermissions


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

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = XDSUserProfileManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        email_verification(self.email)
        return super(XDSUser, self).save(*args, **kwargs)


class XDSConfiguration(TimeStampedModel):
    """Model for XDS Configuration """

    target_xis_metadata_api = models.CharField(
        max_length=200,
        help_text='Enter the XIS api endpoint to query metadata',
        default='http://localhost:8080/api/metadata/')

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('Configuration-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'

    def save(self, *args, **kwargs):
        if not self.pk and XDSConfiguration.objects.exists():
            raise ValidationError('XDSConfiguration model already exists')
        return super(XDSConfiguration, self).save(*args, **kwargs)


class XDSUIConfiguration(TimeStampedModel):
    """Model to contain XDS UI Configuration"""
    search_results_per_page = \
        models.IntegerField(default=10,
                            validators=[MinValueValidator(1,
                                                          "results per page "
                                                          "should be at least "
                                                          "1")])
    xds_configuration = models.OneToOneField(
        XDSConfiguration,
        on_delete=models.CASCADE,
    )
    course_img_fallback = models.ImageField(upload_to='images/',
                                            null=True,
                                            blank=True)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('Configuration-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'

    def save(self, *args, **kwargs):
        if not self.pk and XDSUIConfiguration.objects.exists():
            raise ValidationError('XDSUIConfiguration model already exists')
        return super(XDSUIConfiguration, self).save(*args, **kwargs)


class SearchFilter(TimeStampedModel):
    """Model to contain fields used for filtering search results"""
    FILTER_TYPE_CHOICES = [
        ('terms', 'Checkbox'),
    ]
    display_name = models.CharField(
        max_length=200,
        help_text='Enter the display name of the field to filter on')
    field_name = models.CharField(
        max_length=200,
        help_text='Enter the metadata field name as displayed in Elasticsearch'
                  ' e.g. course.title'
    )
    xds_ui_configuration = models.ForeignKey(XDSUIConfiguration,
                                             on_delete=models.CASCADE)
    filter_type = models.CharField(
        max_length=200,
        choices=FILTER_TYPE_CHOICES,
        default='terms',
    )

    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('Configuration-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'


class SearchSortOption(TimeStampedModel):
    """Model to contain options for sorting search results"""

    display_name = models.CharField(
        max_length=200,
        help_text='Enter the display name of the sorting option')
    field_name = models.CharField(
        max_length=200,
        help_text='Enter the metadata field name as displayed in Elasticsearch'
                  ' e.g. course.title'
    )
    xds_ui_configuration = models \
        .ForeignKey(XDSUIConfiguration, on_delete=models.CASCADE,
                    related_name='search_sort_options')
    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('search-sort-option', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'


class CourseDetailHighlight(TimeStampedModel):
    """Model to contain course detail fields to display on results"""
    HIGHLIGHT_ICON_CHOICES = [
        ('clock', 'clock'),
        ('hourglass', 'hourglass'),
        ('user', 'user'),
        ('multi_users', 'multi_users'),
        ('location', 'location'),
        ('calendar', 'calendar'),
    ]

    display_name = models.CharField(
        max_length=200,
        help_text='Enter the display name of the sorting option')
    field_name = models.CharField(
        max_length=200,
        help_text='Enter the metadata field name as displayed in Elasticsearch'
                  ' e.g. course.title'
    )
    xds_ui_configuration = models \
        .ForeignKey(XDSUIConfiguration, on_delete=models.CASCADE,
                    related_name='course_highlights')
    active = models.BooleanField(default=True)
    highlight_icon = models.CharField(
        max_length=200,
        choices=HIGHLIGHT_ICON_CHOICES,
        default='user',
    )
    rank = \
        models.IntegerField(default=1,
                            help_text="Order in which highlight show on the "
                                      "course detail page (2 items per row)",
                            validators=[MinValueValidator(1,
                                                          "rank shoud be at "
                                                          "least 1")])

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('course-detail-highlight', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'

    def save(self, *args, **kwargs):
        num_active_highlights = \
            CourseDetailHighlight.objects.filter(active=True).count()

        # only 8 highlights can be active at any given time
        if num_active_highlights >= 8:
            # if it's a new record and set to active
            if not self.pk and self.active is True:
                raise ValidationError('Max of 8 active highlight fields has '
                                      'been reached.')
            # updating old record to active
            elif self.active is False:
                raise ValidationError('Max of 8 active highlight fields has '
                                      'been reached.')
            else:
                return super(CourseDetailHighlight, self).save(*args, **kwargs)
        return super(CourseDetailHighlight, self).save(*args, **kwargs)


class CourseSpotlight(TimeStampedModel):
    """Model to define course spotlight objects"""
    course_id = models.CharField(
        max_length=200,
        help_text='Enter the unique Search Engine ID of the course')
    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('course-spotlight', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'


class CourseInformationMapping(TimeStampedModel):
    """ Model to map course information"""

    course_title = models.CharField(max_length=200,
                                    help_text="Enter the title of the course"
                                              "found in the elasticsearch")
    course_description = models.CharField(max_length=200,
                                          help_text="Enter the description of"
                                                    " the course found in the"
                                                    " elasticsearch")
    course_url = models.CharField(max_length=200,
                                  help_text="Enter the url of the course found"
                                            " in the elasticsearch")

    xds_ui_configuration = models \
        .OneToOneField(XDSUIConfiguration,
                       on_delete=models.CASCADE,
                       related_name='course_information')

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('course-information', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'

    def save(self, *args, **kwargs):
        num_active_mappings = CourseInformationMapping.objects.filter().count()

        # if there is more than one
        if num_active_mappings > 1:
            raise ValidationError(
                'Max of 1 active highlight fields has been reached.')

        return super(CourseInformationMapping, self).save(*args, **kwargs)


class Experience(models.Model):
    """Model to store experience instances for interest lists"""

    metadata_key_hash = models.CharField(max_length=200,
                                         primary_key=True)


class InterestList(TimeStampedModel):
    """Model for Interest Lists"""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name="interest_lists")
    description = \
        models.CharField(max_length=200,
                         help_text='Enter a description for the list')
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                         related_name="subscriptions")
    experiences = models.ManyToManyField(Experience,
                                         blank=True)
    name = models.CharField(max_length=200,
                            help_text="Enter the name of the list")


class SavedFilter(TimeStampedModel):
    """Model for Saved Filter"""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name="saved_filters")
    name = models.CharField(max_length=200,
                            help_text="Enter the name of the filter")
    query = models.CharField(max_length=200,
                             help_text="queryString for the filter")


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

        # if current request is in OPEN_ENDPOINTS doesn't check permissions, returns true
        if request.path_info in getattr(settings, 'OPEN_ENDPOINTS', []):
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
            model_meta = lambda: None;
            model_meta.app_label = "core"; \
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
        if not re.findall('\d', password):
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
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                _("The password must contain at least 1 symbol: " +
                  "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 symbol: " +
            "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
        )
