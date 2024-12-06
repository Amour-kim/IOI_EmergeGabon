"""
Configuration WSGI pour le projet.
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Obtenir l'application WSGI
application = get_wsgi_application()

# Ajouter WhiteNoise pour servir les fichiers statiques
application = WhiteNoise(application)
application.add_files('/static/', prefix='static/')
