from django.apps import AppConfig


class DatacenterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.datacenter'
    verbose_name = 'Datacenter'

    def ready(self):
        try:
            import apps.datacenter.signals  # noqa
        except ImportError:
            pass
