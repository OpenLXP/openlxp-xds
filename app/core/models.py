from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.urls import reverse


class XDSConfiguration(models.Model):
    """Model for XDS Configuration """

    target_xis_metadata_api = models.CharField(
        max_length=200,
        help_text='Enter the XIS api endpoint to query metadata')
    search_results_per_page = \
        models.IntegerField(default=10,
                            validators=[MinValueValidator(1, "results per page\
                             should be at least 1")])

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
