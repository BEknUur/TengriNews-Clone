# Project modules
from decouple import config


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
