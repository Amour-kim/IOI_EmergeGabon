from django.apps import AppConfig


class AbonnementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.abonnement'
    verbose_name = 'Abonnement'

    def ready(self):
        try:
            import apps.abonnement.signals  # noqa
        except ImportError:
            pass
