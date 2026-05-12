# Python modules
import os
from celery import Celery

# Project modules
from settings.conf import ENV_ID, ENV_POSSIBLE_OPTIONS

assert ENV_ID in ENV_POSSIBLE_OPTIONS, (
    f"Set correct TENGRI_ENV_ID env var. Possible options: {ENV_POSSIBLE_OPTIONS}"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{ENV_ID}")

app = Celery("tengrinews")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
