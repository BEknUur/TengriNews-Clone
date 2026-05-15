
# ---- builder ----
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev libffi-dev curl ca-certificates \
    graphviz libgraphviz-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем только зависимости для кэширования слоёв (из директории backend)
COPY backend/pyproject.toml backend/poetry.lock* backend/requirements.txt* /app/

RUN python -m pip install --upgrade pip setuptools wheel \
 && if [ -f requirements.txt ]; then \
            # Build wheels including dependencies so runtime install from /wheels succeeds
            pip wheel -r requirements.txt -w /wheels; \
        else \
            echo "requirements.txt not found. Export it (poetry export -f requirements.txt -o requirements.txt)"; \
            exit 1; \
        fi

# ---- runtime ----
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    TENGRI_ENV_ID=prod

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 ca-certificates curl gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip \
 && python -m pip install --no-index --find-links=/wheels -r /app/requirements.txt \
 && rm -rf /wheels

# Копируем проект
# Копируем только код приложения из папки backend
COPY backend/ /app

# Copy entrypoint and make it executable, then ensure ownership
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN useradd --create-home --shell /bin/bash appuser \
 && chown -R appuser:appuser /app

USER appuser
ENV PYTHONPATH=/app

# Use entrypoint to run migrations/collectstatic before CMD
ENTRYPOINT ["/app/entrypoint.sh"]

# Опционально: сделайте исполняемым /app/entrypoint.sh если добавите
EXPOSE 8000

# По умолчанию запускаем gunicorn с uvicorn worker (ASGI). Для Daphne используйте CMD ниже.
CMD ["gunicorn", "settings.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]

# Альтернативный CMD для Daphne (Channels):
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "settings.asgi:application"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://127.0.0.1:8000/healthz || exit 1

