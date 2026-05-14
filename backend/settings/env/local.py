# Project modules
from settings.base import *  # noqa: F403

DEBUG: bool = True

ALLOWED_HOSTS: list = ["*"]

CORS_ALLOW_ALL_ORIGINS: bool = True
CORS_ALLOW_CREDENTIALS: bool = True

# Database configuration
DATABASES: dict = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "localdb.sqlite3",
    },
}

# Caching configuration
CACHES: dict = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "tengrinews-local-cache",
    }
}

# Use eager Celery tasks in local/test mode to avoid broker dependency.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Keep local/test API runs deterministic without throttle state bleed.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # type: ignore[name-defined] # noqa: F405
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {},
}

DISABLE_AUTH_THROTTLING = True
