from django.apps import AppConfig

class TutoratConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tutorat'
    verbose_name = 'Gestion du Tutorat'

    def ready(self):
        import apps.tutorat.signals  # noqa
