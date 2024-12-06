import os
from celery import Celery
from django.conf import settings

# Définir les paramètres par défaut de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Créer l'application Celery
app = Celery('gabon_edu')

# Configuration de Celery depuis les paramètres Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger les tâches des applications Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    """Tâche de test pour Celery"""
    print(f'Request: {self.request!r}')
