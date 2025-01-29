from django.apps import AppConfig


class XdsApiConfig(AppConfig):
    name = 'xds_api'

    def ready(self):
        import xds_api.signals
        xds_api.signals.add_permissions
        return super().ready()
