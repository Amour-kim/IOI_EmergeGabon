from django.apps import AppConfig

class CommunityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.community'
    verbose_name = 'Communautés'

    def ready(self):
        import apps.community.signals  # noqa
