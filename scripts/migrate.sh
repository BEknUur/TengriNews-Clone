#!/usr/bin/env bash
set -euo pipefail

cd backend
uv run python manage.py makemigrations
uv run python manage.py migrate
