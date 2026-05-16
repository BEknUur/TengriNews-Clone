#!/usr/bin/env bash
set -euo pipefail

cd backend
uv run ruff check --fix apps/ settings/
