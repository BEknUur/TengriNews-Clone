# Project modules
from decouple import config


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 200


ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)

ENV_ID = config("TENGRI_ENV_ID", default="local", cast=str)

POSTGRESQL_URL = config(
    "POSTGRESQL_URL",
    default="postgres://myuser:mypassword@localhost:5432/mydatabase",
    cast=str,
)

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-b@wp(sggy#_@61*7gxq5-yxu)y54&t1w#f*f2dbkq(f0kc=1qo",
    cast=str,
)

REDIS_HOST = config("REDIS_HOST", default="localhost", cast=str)
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_DB = config("REDIS_DB", default=0, cast=int)
