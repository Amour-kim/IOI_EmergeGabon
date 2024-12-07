from django.apps import AppConfig

class EvenementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.evenements'
    verbose_name = 'Gestion des Événements'

    def ready(self):
        import apps.evenements.signals  # noqa
