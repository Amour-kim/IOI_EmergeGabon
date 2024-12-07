from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BibliothequeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bibliotheque'
    verbose_name = _("Bibliothèque numérique")

    def ready(self):
        import apps.bibliotheque.signals
