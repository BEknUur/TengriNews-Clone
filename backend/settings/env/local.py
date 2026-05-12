# Project modules
from settings.base import *  # noqa: F403
from settings.conf import REDIS_HOST, REDIS_PORT, REDIS_DB

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "localdb.sqlite3",
    },
}

# Caching configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
