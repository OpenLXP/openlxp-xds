from django.db import models

from django.urls import reverse
from django.forms import ValidationError


class XDSConfiguration(models.Model):
    """Model for XDS Configuration """

    target_xis_es_api = models.CharField(
        max_length=200,
        help_text='Enter the XIS api endpoint to query ElasticSearch')
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
        