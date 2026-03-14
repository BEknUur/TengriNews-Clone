FROM python:3.12-slim

WORKDIR /backend

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend/pyproject.toml ./
COPY ./backend .

RUN uv pip install --system --no-cache . \
    && rm -rf /root/.cache

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn settings.wsgi:application --bind 0.0.0.0:8000"]