import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OrderingSystem.settings')

import django
django.setup()  # ✅ Ensure apps are loaded

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter


# Import this AFTER django.setup()
from MSMEOrderingWebApp.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
