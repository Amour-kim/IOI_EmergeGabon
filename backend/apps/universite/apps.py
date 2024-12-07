from django.apps import AppConfig


class UniversiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.universite'
    verbose_name = 'Université'

    def ready(self):
        try:
            import apps.universite.signals  # noqa
        except ImportError:
            pass
