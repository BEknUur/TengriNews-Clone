"""Production settings — loaded when TENGRI_ENV_ID=prod."""

# Third-party modules
import dj_database_url
from decouple import Csv, config

# Project modules
from settings.base import *  # noqa: F403
from settings.conf import POSTGRESQL_URL, REDIS_DB, REDIS_HOST, REDIS_PORT

DEBUG: bool = False

ALLOWED_HOSTS: list[str] = config(
    "ALLOWED_HOSTS",
    cast=Csv(),
    default="localhost,127.0.0.1,212.109.223.106",
)

DATABASES: dict = {
    "default": dj_database_url.parse(
        POSTGRESQL_URL,
    )
}

STATICFILES_STORAGE: str = "whitenoise.storage.CompressedStaticFilesStorage"

CORS_ALLOWED_ORIGINS: list[str] = config(
    "CORS_ALLOWED_ORIGINS",
    cast=Csv(),
    default="http://localhost,http://localhost:80,http://localhost:5173,http://localhost:8000,http://127.0.0.1:81,http://212.109.223.106:81",
)
CSRF_TRUSTED_ORIGINS: list[str] = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=Csv(),
    default="http://localhost,http://localhost:80,http://localhost:5173,http://localhost:8000,http://127.0.0.1:81,http://212.109.223.106:81",
)
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
CACHES["article_cache"] = {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
}
