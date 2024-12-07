from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DepartementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.departements'
    verbose_name = _("Départements")

    def ready(self):
        import apps.departements.signals
