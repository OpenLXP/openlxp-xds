from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from model_utils.models import TimeStampedModel
from openlxp_notifications.management.utils.notification import \
    email_verification


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


class XDSUser(AbstractUser):
    """Model for a user"""

    # User attributes
    username = None
    email = models.EmailField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

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
