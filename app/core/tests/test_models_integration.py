from django.core.exceptions import ValidationError
from django.test import TestCase, tag

from core.models import XDSConfiguration


@tag('integration')
class ModelTests(TestCase):

    def test_create_two_xds_configuration(self):
        """Test that trying to create more than one XDS Configuration objects
            throws ValidationError """
        with self.assertRaises(ValidationError):
            xdsConfig = XDSConfiguration(target_xis_metadata_api="test",
                                         search_results_per_page=15)
            xdsConfig2 = XDSConfiguration(target_xis_metadata_api="test2",
                                          search_results_per_page=3)
            xdsConfig.save()
            xdsConfig2.save()

    def test_xds_config_rpp_validator(self):
        """Test that creating an XSD config object with a value lower than the
            min value triggers a validation error"""
        xdsConfig = XDSConfiguration(target_xis_metadata_api="test",
                                     search_results_per_page=0)
        self.assertRaises(ValidationError, xdsConfig.full_clean)

    def test_xds_config_save_success(self):
        """Test that creating an XDS config object with correct values passes
            validation"""
        xdsConfig = XDSConfiguration(target_xis_metadata_api="test",
                                     search_results_per_page=3)
        xdsConfig.save()
        retrievedObj = XDSConfiguration.objects.first()

        self.assertEqual(retrievedObj.search_results_per_page, 3)
        self.assertEqual(retrievedObj.target_xis_metadata_api, "test")
