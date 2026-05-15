#!/usr/bin/env bash
set -euo pipefail

# Entrypoint для Docker-контейнера Django
# Поведение:
# - Пытается выполнить миграции повторно до успешного выполнения (с таймаутом)
# - Опционально собирает статику при COLLECT_STATIC=1
# - Выполняет переданную команду (exec "$@")

MAX_TRIES=${MAX_TRIES:-30}
SLEEP_INTERVAL=${SLEEP_INTERVAL:-2}

echo "Waiting for database and applying migrations (up to $MAX_TRIES attempts)..."
i=0
until python manage.py migrate --noinput; do
  i=$((i+1))
  if [ "$i" -ge "$MAX_TRIES" ]; then
    echo "Database migration failed after $MAX_TRIES attempts." >&2
    exit 1
  fi
  echo "Database not ready, retrying in ${SLEEP_INTERVAL}s... ($i/$MAX_TRIES)"
  sleep "$SLEEP_INTERVAL"
done

if [ "${COLLECT_STATIC:-0}" = "1" ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi

echo "Entrypoint finished, executing command: $@"
exec "$@"
