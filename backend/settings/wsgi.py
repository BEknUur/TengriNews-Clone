# Python modules
import os

# Project modules
from settings.conf import ENV_POSSIBLE_OPTIONS, ENV_ID
from django.core.wsgi import get_wsgi_application

assert ENV_ID in ENV_POSSIBLE_OPTIONS, (
    f"Set correct TENGRI_ENV_ID env var. Possible options: {ENV_POSSIBLE_OPTIONS}"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.base")

application = get_wsgi_application()
