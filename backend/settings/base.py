"""Base Django settings for TengriNews Clone project."""

# Python modules
import os
from datetime import timedelta

# Third-party modules
from celery.schedules import crontab

# Project modules
from settings.conf import *  # noqa: F403

"""
Path configurations
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
ROOT_URLCONF = "settings.urls"
WSGI_APPLICATION = "settings.wsgi.application"
ASGI_APPLICATION = "settings.asgi.application"
AUTH_USER_MODEL = "accounts.CustomUser"

"""
Apps
"""

DJANGO_AND_THIRD_PARTY_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "django_extensions",
]

PROJECT_APPS = [
    "apps.abstracts.apps.AbstractConfig",
    "apps.main.apps.MainConfig",
    "apps.accounts.apps.AccountsConfig",
]

INSTALLED_APPS = DJANGO_AND_THIRD_PARTY_APPS + PROJECT_APPS


"""
Logging
"""

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
        "verbose": {
            "format": "[{asctime}] {levelname} "
            "{name} {module}.{funcName}: {lineno} - {message}",
            "style": "{",
        },
        "json": {
            "format": "{message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "filename": "logs/app.log",
            "maxBytes": 5 * 1024 * 1024,  # 10 MB
            "backupCount": 3,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "debug_only": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filename": "logs/debug_requests.log",
            "maxBytes": 5 * 1024 * 1024,  # 10 MB
            "backupCount": 3,
            "formatter": "verbose",
            "filters": ["require_debug_true"],
            "encoding": "utf-8",
        },
        "request_json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filename": "logs/requests.jsonl",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "apps.users": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.blog": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file", "debug_only"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps.requests": {
            "handlers": ["console", "request_json_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

"""
Simple JWT
"""

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,  # noqa: F405
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

"""
Django Rest Framework
"""

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "apps.abstracts.trottling.CustomAnonRateThrottle",
        "apps.abstracts.trottling.CustomUserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "auth_login": "5/minute",
        "auth_register": "10/hour",
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "TengriNews Clone API",
    "DESCRIPTION": "REST API documentation for TengriNews Clone.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "displayOperationId": True,
        "defaultModelsExpandDepth": 1,
    },
}


"""
Middleware | Templates | Validators
"""

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "apps.abstracts.ratelimit.RateLimitMiddleware",
    "apps.abstracts.middleware.StructuredRequestLoggingMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.abstracts.middleware.CurrentUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


"""
Unfold configuration
"""

UNFOLD = {
    "SITE_TITLE": "Tengri News Admin Panel",
    "SITE_HEADER": "Tengri News Admin Panel",
    "SITE_SYMBOL": "dashboard",
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


"""
Internalizations
"""

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


"""
Celery configuration
"""


CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"  # noqa: F405
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"  # noqa: F405
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = TIME_ZONE

CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_REJECT_ON_WORKER_LOST = True

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"],  # noqa: F405
        },
    },
}

CELERY_BEAT_SCHEDULE = {
    "cleanup_soft_deleted_records": {
        "task": "apps.abstracts.tasks.cleanup_soft_deleted_records",
        "schedule": crontab(hour=3, minute=0),
    },
    "collect_content_statistics": {
        "task": "apps.abstracts.tasks.collect_content_statistics",
        "schedule": crontab(hour=3, minute=0),
    },
}

"""
Static | Media
"""

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
