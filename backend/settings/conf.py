from decouple import config

DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 200

ENV_ID: str = config("TENGRI_ENV_ID", default="local")
ENV_POSSIBLE_OPTIONS: list[str] = ["local", "prod"]

SECRET_KEY: str = config(
    "SECRET_KEY",
    default="django-insecure-b@wp(sggy#_@61*7gxq5-yxu)y54&t1w#f*f2dbkq(f0kc=1qo",
)

POSTGRESQL_URL: str = config(
    "POSTGRESQL_URL",
    default="postgres://myuser:mypassword@localhost:5432/mydatabase",
)

REDIS_HOST: str = config("REDIS_HOST", default="localhost")
REDIS_PORT: int = config("REDIS_PORT", default=6379, cast=int)
REDIS_DB: int = config("REDIS_DB", default=0, cast=int)
