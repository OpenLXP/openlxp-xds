from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        super(CoreConfig, self).ready()
        import core.signals
        core.signals.interest_list_notify
