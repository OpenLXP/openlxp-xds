from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from model_utils.models import TimeStampedModel


class XDSConfiguration(TimeStampedModel):
    """Model for XDS Configuration """

    target_xis_metadata_api = models.CharField(
        max_length=200,
        help_text='Enter the XIS api endpoint to query metadata')

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
    course_img_fallback = models.ImageField(upload_to='images/', null=True)

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
    xds_ui_configuration = models\
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
        ('multi-users', 'multi-users'),
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
    xds_ui_configuration = models\
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
