"""
Configuration ASGI pour le projet.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Obtenir l'application ASGI
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # HTTP
    "http": django_asgi_app,
    
    # WebSocket avec authentification
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # Les routes WebSocket seront ajoutées ici
        ])
    ),
})
