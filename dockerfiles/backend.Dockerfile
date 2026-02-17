FROM python:3.12-slim

WORKDIR /backend

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY ../backend/pyproject.toml ./

RUN uv pip install --system --no-cache . \
    && rm -rf /root/.cache

COPY ./backend .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn settings.wsgi:application --bind 0.0.0.0:8000"]