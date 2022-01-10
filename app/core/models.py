from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from model_utils.models import TimeStampedModel
from configurations.models import XDSUIConfiguration


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


# class PermissionsChecker(DjangoModelPermissions):
#     """
#     Class to define the method for checking permissions for the XDS API
#     """
#     perms_map = {
#         'GET': ['%(app_label)s.view_%(model_name)s'],
#         'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
#         'POST': ['%(app_label)s.add_%(model_name)s'],
#         'PUT': ['%(app_label)s.change_%(model_name)s'],
#         'PATCH': ['%(app_label)s.change_%(model_name)s'],
#         'DELETE': ['%(app_label)s.delete_%(model_name)s'],
#     }

#     def has_permission(self, request, view):
#         # Workaround to ensure DjangoModelPermissions are not applied
#         # to the root view when using DefaultRouter.
#         if getattr(view, '_ignore_model_permissions', False):
#             return True

#         # if current request is in OPEN_ENDPOINTS doesn't check permissions,
#         # returns true
#         if request.path_info in getattr(settings, 'OPEN_ENDPOINTS', []):
#             return True

#         # checks if there is a logged in user
#         if not request.user or (
#                 not request.user.is_authenticated and
#                 self.authenticated_users_only):
#             return False

#         try:
#             # tries to get app and model names from view
#             model_meta = self._queryset(view).model._meta

#         except Exception:
#             # if unable, generates app and model names
#             def model_meta():
#                 return None

#             model_meta.app_label = "core"
#             model_meta.model_name = \
#                 view.get_view_name().lower().replace(' ', '')

#         # determines permission required to access this endpoint
#         perms = self.get_required_permissions(request.method, model_meta)

#         # checks if the user has the required permission
#         return request.user.has_perms(perms)

#     def get_required_permissions(self, method, model_meta):
#         """
#         Given a model and an HTTP method, return the list of permission
#         codes that the user is required to have.
#         """
#         kwargs = {
#             'app_label': model_meta.app_label,
#             'model_name': model_meta.model_name
#         }

#         if method not in self.perms_map:
#             raise exceptions.MethodNotAllowed(method)

#         return [perm % kwargs for perm in self.perms_map[method]]


# class NumberValidator(object):
#     def validate(self, password, user=None):
#         if not re.findall('\\d', password):
#             raise ValidationError(
#                 _("The password must contain at least 1 digit, 0-9."),
#                 code='password_no_number',
#             )

#     def get_help_text(self):
#         return _(
#             "Your password must contain at least 1 digit, 0-9."
#         )


# class UppercaseValidator(object):
#     def validate(self, password, user=None):
#         if not re.findall('[A-Z]', password):
#             raise ValidationError(
#                 _(
#                     "The password must contain at least 1 uppercase letter, "
#                     "A-Z."),
#                 code='password_no_upper',
#             )

#     def get_help_text(self):
#         return _(
#             "Your password must contain at least 1 uppercase letter, A-Z."
#         )


# class LowercaseValidator(object):
#     def validate(self, password, user=None):
#         if not re.findall('[a-z]', password):
#             raise ValidationError(
#                 _(
#                     "The password must contain at least 1 lowercase letter, "
#                     "a-z."),
#                 code='password_no_lower',
#             )

#     def get_help_text(self):
#         return _(
#             "Your password must contain at least 1 lowercase letter, a-z."
#         )


# class SymbolValidator(object):
#     def validate(self, password, user=None):
#         if not re.findall('[()[\\]{}|\\\\`~!@#$%^&*_\\-+=;:\'",<>./?]',
#                           password):
#             raise ValidationError(
#                 _("The password must contain at least 1 symbol: " +
#                   "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?"),
#                 code='password_no_symbol',
#             )

#     def get_help_text(self):
#         return _(
#             "Your password must contain at least 1 symbol: " +
#             "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?"
#         )
