"""
ASGI config for grabit project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import listings.routing
import chat.routing  # ✅ Import chat WebSocket routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grabit.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            listings.routing.websocket_urlpatterns +  # ✅ Include listings WebSocket routes
            chat.routing.websocket_urlpatterns  # ✅ Include chat WebSocket routes
        )
    ),
})
