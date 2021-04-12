from django.core.exceptions import ValidationError
from django.test import TestCase, tag

from core.models import XDSConfiguration, XDSUIConfiguration


@tag('integration')
class ModelTests(TestCase):

    def test_create_two_xds_configuration(self):
        """Test that trying to create more than one XDS Configuration objects
            throws ValidationError """
        with self.assertRaises(ValidationError):
            xdsConfig = XDSConfiguration(target_xis_metadata_api="test")
            xdsConfig2 = XDSConfiguration(target_xis_metadata_api="test2")
            xdsConfig.save()
            xdsConfig2.save()

    def test_xds_ui_config_rpp_validator(self):
        """Test that creating an XSD config object with a value lower than the
            min value triggers a validation error"""
        xds_config = XDSConfiguration(target_xis_metadata_api="test")
        xds_ui_config = XDSUIConfiguration(search_results_per_page=-1,
                                           xds_configuration=xds_config)
        self.assertRaises(ValidationError, xds_ui_config.full_clean)

    def test_xds_config_save_success(self):
        """Test that creating an XDS config object with correct values passes
            validation"""
        xdsConfig = XDSConfiguration(target_xis_metadata_api="test")
        xdsConfig.save()
        retrievedObj = XDSConfiguration.objects.first()

        self.assertEqual(retrievedObj.target_xis_metadata_api, "test")
