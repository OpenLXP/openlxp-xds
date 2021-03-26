from django.test import SimpleTestCase, tag

from core.models import SearchFilter, XDSConfiguration, XDSUIConfiguration


@tag('unit')
class ModelTests(SimpleTestCase):

    def test_create_xds_configuration(self):
        """Test that creating a new XDS Configuration entry is successful\
        with defaults """
        xdsConfig = XDSConfiguration(target_xis_metadata_api="test")

        self.assertEqual(xdsConfig.target_xis_metadata_api, "test")

    def test_create_xds_ui_configuration(self):
        """Test that creating a new XDSUI Configuration is successful with \
            defaults"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)

        self.assertEqual(uiConfig.search_results_per_page, 10)

    def test_create_search_filter(self):
        """Test that creating a search filter object works correctly"""
        config = XDSConfiguration(target_xis_metadata_api="test")
        uiConfig = XDSUIConfiguration(xds_configuration=config)
        sf = SearchFilter(display_name="test",
                          field_name="test",
                          xds_ui_configuration=uiConfig)
        self.assertEqual(sf.xds_ui_configuration, uiConfig)
