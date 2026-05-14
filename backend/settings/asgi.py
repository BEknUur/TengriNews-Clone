# Python modules
import os

# Django modules
from django.core.asgi import get_asgi_application

# Third-party modules
from channels.routing import ProtocolTypeRouter, URLRouter

# Project modules
from apps.main.routing import websocket_urlpatterns
from settings.conf import ENV_ID, ENV_POSSIBLE_OPTIONS

assert (
    ENV_ID in ENV_POSSIBLE_OPTIONS
), f"Set correct TENGRI_ENV_ID env var. Possible options: {ENV_POSSIBLE_OPTIONS}"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{ENV_ID}")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
