import json
from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import XDSConfiguration, XDSUIConfiguration


@tag('unit')
class ViewTests(APITestCase):

    def test_xds_ui_config_view(self):
        """Test that making a GET request to the api gives us a JSON of the
            stored XDSUIConfiguration model"""
        url = reverse('xds_api:xds-ui-configuration')
        with patch('xds_api.views.XDSUIConfiguration.objects') as xds_ui_Obj:
            xds_config = XDSConfiguration(target_xis_metadata_api="test")
            xds_ui_cfg = XDSUIConfiguration(search_results_per_page=10,
                                            xds_configuration=xds_config)
            xds_ui_Obj.return_value = xds_ui_Obj
            xds_ui_Obj.first.return_value = xds_ui_cfg

            response = self.client.get(url)
            response_dict = json.loads(response.content)
            print(response.content)

            self.assertEqual(response_dict['search_results_per_page'],
                             xds_ui_cfg.search_results_per_page)
            self.assertEqual(response_dict['search_sort_options'], [])
            self.assertEqual(response.status_code, status.HTTP_200_OK)
