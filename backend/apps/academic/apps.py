from django.apps import AppConfig

class AcademicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.academic'
    verbose_name = 'Gestion académique'

    def ready(self):
        import apps.academic.signals  # noqa
