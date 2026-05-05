import os

# ✅ MUST be first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# ✅ Setup Django BEFORE importing app code
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# ✅ NOW safe to import Channels + your code
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from matching.consumers import ChatConsumer


application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": URLRouter([
        path("ws/chat/<uuid:session_id>/", ChatConsumer.as_asgi()),
    ]),
})