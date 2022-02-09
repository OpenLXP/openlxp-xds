import logging

import requests
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from model_utils.models import TimeStampedModel
from users.models import Organization

logger = logging.getLogger('dict_config_logger')


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
        super(XDSConfiguration, self).save(*args, **kwargs)
        try:
            api_url = self.target_xis_metadata_api.replace(
                'metadata', 'catalogs')
            response = requests.get(api_url)
            responseJSON = response.json()
            for catalog in responseJSON:
                if not Organization.objects.filter(filter=catalog).exists():
                    Organization.objects.create(name=catalog, filter=catalog)
        except Exception:
            logger.log("Error loading catalogs from XIS")


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
