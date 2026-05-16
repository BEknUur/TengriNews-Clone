.PHONY: install run shell \
superuser \
migrations migrate showmigrations seed \
erd \
test test-v coverage \
lint lint-fix \
up down logs build clean all \
worker beat \
frontend-install frontend-dev frontend-build

PYTHON = .venv/bin/python
UV = uv
SETTINGS = settings.env.local
APP = settings.celery:app

install:
	cd backend && $(UV) sync --all-groups

run:
	cd backend && $(PYTHON) manage.py runserver --settings=$(SETTINGS)

shell:
	cd backend && $(PYTHON) manage.py shell --settings=$(SETTINGS)

superuser:
	cd backend && $(PYTHON) manage.py createsuperuser --settings=$(SETTINGS)

migrations:
	cd backend && $(PYTHON) manage.py makemigrations --settings=$(SETTINGS)

migrate:
	cd backend && $(PYTHON) manage.py migrate --settings=$(SETTINGS)

showmigrations:
	cd backend && $(PYTHON) manage.py showmigrations --settings=$(SETTINGS)

seed:
	cd backend && $(PYTHON) manage.py seed_data --settings=$(SETTINGS)

erd:
	docker compose run --rm backend python manage.py graph_models -a -g -o /app/er_diagram.png --settings=$(SETTINGS)

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

lint:
	cd backend && $(PYTHON) -m ruff check apps/ settings/

lint-fix:
	cd backend && $(PYTHON) -m ruff check --fix apps/ settings/

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

worker:
	cd backend && $(PYTHON) -m celery -A $(APP) worker --loglevel=info

beat:
	cd backend && $(PYTHON) -m celery -A $(APP) beat --loglevel=info

test:
	cd backend && $(PYTHON) -m pytest -q

test-v:
	cd backend && $(PYTHON) -m pytest -v

coverage:
	cd backend && $(PYTHON) -m pytest --cov=apps --cov-report=term-missing
