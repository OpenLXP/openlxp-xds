import json

from core.models import SearchSortOption, XDSConfiguration, XDSUIConfiguration
from django.test import tag
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


@tag('integration')
class ViewTests(APITestCase):

    def test_xds_ui_config_view(self):
        """Test that making a GET request to the api gives us a JSON of the
            stored XDSUIConfiguration model AND its sort options"""
        url = reverse('xds_api:xds-ui-configuration')
        xds_config = XDSConfiguration(target_xis_metadata_api="test")
        xds_ui_cfg = XDSUIConfiguration(search_results_per_page=10,
                                        xds_configuration=xds_config)
        sort_option = SearchSortOption(display_name="test",
                                       field_name="test-field",
                                       xds_ui_configuration=xds_ui_cfg,
                                       active=True)
        sort_option2 = SearchSortOption(display_name="test-2",
                                        field_name="test-field-2",
                                        xds_ui_configuration=xds_ui_cfg,
                                        active=True)

        xds_config.save()
        xds_ui_cfg.save()
        sort_option.save()
        sort_option2.save()

        response = self.client.get(url)
        response_dict = json.loads(response.content)

        print(response_dict)

        self.assertEqual(response_dict['search_results_per_page'],
                         xds_ui_cfg.search_results_per_page)
        self.assertEqual(len(response_dict['search_sort_options']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
