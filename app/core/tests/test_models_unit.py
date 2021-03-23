from django.test import SimpleTestCase, tag

from core.models import XDSConfiguration


@tag('unit')
class ModelTests(SimpleTestCase):

    def test_create_xds_configuration(self):
        """Test that creating a new XDS Configuration entry is successful
        with defaults """
        xdsConfig = XDSConfiguration(target_xis_metadata_api="test")

        self.assertEqual(xdsConfig.target_xis_metadata_api, "test")
        self.assertEqual(xdsConfig.search_results_per_page, 10)
