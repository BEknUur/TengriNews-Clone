"""Production settings — loaded when TENGRI_ENV_ID=prod."""

# Third-party modules
import dj_database_url

# Project modules
from settings.base import *  # noqa: F403
from settings.conf import POSTGRESQL_URL, REDIS_DB, REDIS_HOST, REDIS_PORT

DEBUG: bool = False

ALLOWED_HOSTS: list[str] = [
    "localhost:8000",
    "localhost",
    "localhost:5173",
]

DATABASES: dict = {
    "default": dj_database_url.parse(
        POSTGRESQL_URL,
    )
}

STATICFILES_STORAGE: str = "whitenoise.storage.CompressedStaticFilesStorage"

CORS_ALLOWED_ORIGINS: list[str] = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:5173",
    "http://localhost:8000",
]
CORS_ALLOW_CREDENTIALS: bool = True

CACHES: dict = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
