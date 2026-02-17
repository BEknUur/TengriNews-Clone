# Project modules
from settings.conf import POSTGRESQL_URL
from settings.base import *  # noqa F401

# Third-party modules
import dj_database_url


DEBUG = False
ALLOWED_HOSTS = ["localhost:8000", "localhost", "localhost:5173"]

DATABASES = {
    "default": dj_database_url.config(
        default=POSTGRESQL_URL,
    )
}

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:5173",
    "http://localhost:8000",
]
CORS_ALLOW_CREDENTIALS = True
