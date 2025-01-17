import logging

from django.contrib.auth.models import Group
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ValidationError
from django.urls import reverse
from model_utils.models import TimeStampedModel

from es_api.utils.queries_base import BaseQueries
from users.models import Organization, XDSUser

logger = logging.getLogger('dict_config_logger')


class XDSConfiguration(TimeStampedModel):
    """Model for XDS Configuration """

    target_xis_metadata_api = models.CharField(
        max_length=200,
        help_text='Enter the XIS api endpoint to query metadata',
        default='http://localhost:8080/api/metadata/')

    target_xse_host = models.CharField(
        max_length=200,
        help_text='Enter the XSE Host to search',
        default='http://localhost:9200')
    target_xse_index = models.CharField(
        max_length=200,
        help_text='Enter the XSE Index to search',
        default='metadata')
    default_user_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        help_text='Select the group to assign new users to',
        blank=True,
        null=True
    )
    lrs_endpoint = models.CharField(
        max_length=200,
        help_text='Enter the xAPI LRS Endpoint to send data to',
        blank=True,
        null=True
    )
    lrs_username = models.CharField(
        max_length=200,
        help_text='Enter the xAPI LRS HTTP Basic Auth username',
        blank=True,
        null=True
    )
    lrs_password = models.CharField(
        max_length=200,
        help_text='Enter the xAPI LRS HTTP Basic Auth password',
        blank=True,
        null=True
    )

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
            queries = BaseQueries(self.target_xse_host, self.target_xse_index)
            responseJSON = queries.filter_options()
            for catalog in responseJSON:
                if not Organization.objects.filter(filter=catalog).exists():
                    Organization.objects.create(name=catalog, filter=catalog)
        except Exception:
            logger.info("Error loading catalogs from XSE")


@receiver(post_save, sender=XDSUser)
def add_default_group(sender, instance, created, **kwargs):
    """
    Adds new users to a default group specified in XDSConfiguration
    Note: not applied to users created through admin panel, as they manually
    select groups for the new user
    """
    # if new and default_user_group from XDSConfig is defined
    if created and len(XDSConfiguration.objects.all()) > 0 and \
            XDSConfiguration.objects.first().default_user_group is not None:
        base_permission_group = XDSConfiguration.objects.first() \
            .default_user_group
        # add the new user to that group
        instance.groups.add(base_permission_group)
        instance.save()


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
    ui_logo = models.ImageField(upload_to='images/',
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
    """ Model to map course information for UI"""

    course_title = models.CharField(max_length=200,
                                    default="Course.CourseTitle",
                                    help_text="Enter the mapping for the "
                                              "title of the course found in "
                                              "the elasticsearch")
    course_description = models.CharField(max_length=200,
                                          default="Course."
                                                  "CourseShortDescription",
                                          help_text="Enter the mapping for the"
                                                    " description of"
                                                    " the course found in the"
                                                    " elasticsearch")
    course_url = models.CharField(max_length=200,
                                  default="Course.CourseURL",
                                  help_text="Enter the mapping for the "
                                            "url of the course found"
                                            " in the elasticsearch")

    course_code = models.CharField(max_length=200,
                                   default="Course.CourseCode",
                                   help_text="Enter the mapping for the "
                                             "code of the course "
                                             "found in the elasticsearch")

    course_startDate = models.CharField(max_length=200,
                                        default="Course_Instance.StartDate",
                                        help_text="Enter the mapping for the "
                                                  "start date of"
                                                  " the course found in the"
                                                  " elasticsearch")
    course_endDate = models.CharField(max_length=200,
                                      default="Course_Instance.EndDate",
                                      help_text="Enter the mapping for the "
                                                "end date of"
                                                " the course found in the"
                                                " elasticsearch")

    course_provider = models.CharField(max_length=200,
                                       default="Course.CourseProviderName",
                                       help_text="Enter the mapping for the "
                                                 "provider of"
                                                 " the course found in the"
                                                 " elasticsearch")

    course_instructor = models.CharField(max_length=200,
                                         default="Course_Instance.Instructor",
                                         help_text="Enter the mapping for the "
                                                   "instructor of"
                                                   " the course found in the"
                                                   " elasticsearch")

    course_deliveryMode = models.CharField(max_length=200,
                                           default="Course_Instance."
                                                   "DeliveryMode",
                                           help_text="Enter the mapping for "
                                                     "the delivery mode of"
                                                     " the course found in the"
                                                     " elasticsearch")

    course_type = models.CharField(max_length=200,
                                   default="Course."
                                   "CourseType",
                                   help_text="Enter the mapping for "
                                             "the Course type of"
                                             " the course found in the"
                                             " elasticsearch")

    course_time = models.CharField(max_length=200,
                                   default="Course."
                                   "EstimatedCompletionTime",
                                   help_text="Enter the mapping for "
                                             "the estimated completion time "
                                             " for the course found in the"
                                             " elasticsearch")

    course_thumbnail = models.CharField(max_length=200,
                                        default="Technical_Information."
                                                "Thumbnail",
                                        help_text="Enter the mapping for the "
                                                  "thumbnail of"
                                                  " the course found in the"
                                                  " elasticsearch")

    course_derived_from = models.CharField(max_length=200,
                                           default="P2881-Core.DerivedFrom",
                                           help_text="Enter the mapping for "
                                           "the reference to the "
                                           "course derived from found in the"
                                           " elasticsearch")

    course_competency = models.CharField(max_length=200,
                                         default="Course."
                                         "CourseLearningOutcome",
                                         help_text="Enter the mapping for "
                                         "the reference to the "
                                         "competency taught")

    course_subject = models.CharField(max_length=200,
                                      default="p2881-core.Subject",
                                      help_text="Enter the mapping for "
                                      "the course subject")

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
