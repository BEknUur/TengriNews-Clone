.PHONY: install run shell \
superuser \
migrations migrate showmigrations seed \
test test-v \
lint lint-fix \
up down logs build clean all \
worker beat

# config
PYTHON = backend/.venv/bin/python
UV = uv
MANAGE = $(PYTHON) backend/manage.py
SETTINGS = settings.env.local
APP = settings.celery:app

# install
install:
	cd backend && $(UV) pip install -e .

# django
run:
	cd backend && $(PYTHON) manage.py runserver --settings=$(SETTINGS)

shell:
	cd backend && $(PYTHON) manage.py shell --settings=$(SETTINGS)

superuser:
	cd backend && $(PYTHON) manage.py createsuperuser --settings=$(SETTINGS)

# migrations
migrations:
	cd backend && $(PYTHON) manage.py makemigrations --settings=$(SETTINGS)

migrate:
	cd backend && $(PYTHON) manage.py migrate --settings=$(SETTINGS)

showmigrations:
	cd backend && $(PYTHON) manage.py showmigrations --settings=$(SETTINGS)

seed:
	cd backend && $(PYTHON) manage.py seed_data --settings=$(SETTINGS)

# docker
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down -v

all:
	docker compose up --build -d

# tests
test:
	cd backend && $(PYTHON) -m pytest

test-v:
	cd backend && $(PYTHON) -m pytest -v

# lint
lint:
	cd backend && $(PYTHON) -m ruff check apps/ settings/

lint-fix:
	cd backend && $(PYTHON) -m ruff check --fix apps/ settings/

# celery
worker:
	cd backend && $(PYTHON) -m celery -A $(APP) worker --loglevel=info

beat:
	cd backend && $(PYTHON) -m celery -A $(APP) beat --loglevel=info