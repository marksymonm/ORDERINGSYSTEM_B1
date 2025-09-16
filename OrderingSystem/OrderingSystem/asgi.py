import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OrderingSystem.settings')

# Standard ASGI application for HTTP
django_asgi_app = get_asgi_application()

# Import websocket URL patterns AFTER settings are configured
from MSMEOrderingWebApp.routing import websocket_urlpatterns

# ProtocolTypeRouter to handle HTTP + WebSockets
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
