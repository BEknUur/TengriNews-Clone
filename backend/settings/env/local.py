# Project modules
from settings.base import *  # noqa: F403
from settings.conf import REDIS_HOST, REDIS_PORT, REDIS_DB

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
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
