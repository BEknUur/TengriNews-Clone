# TengriNews-Clone — Task Board

## Что уже реализовано

- [x] Модели: User, Category, Tag, Article, Comment, Reaction (soft delete)
- [x] JWT аутентификация (SimpleJWT: login, register, refresh)
- [x] Permissions RBAC (IsAdminOnly, IsEditorOrAdmin, IsAuthorOrEditorOrAdmin и др.)
- [x] Pagination (Cursor, PageNumber, LimitOffset)
- [x] Filtering & Search (django-filter, SearchFilter, OrderingFilter)
- [x] DB Indexes (is_published, composite [published_at, id])
- [x] DRF Serializers (nested, read/write разделены)
- [x] OpenAPI docs (drf-spectacular, Swagger UI на /api/docs/)
- [x] Django Admin (django-unfold)
- [x] Docker + Compose (backend + postgres)
- [x] Тесты (pytest: auth, articles, categories, comments, tags, reactions)
- [x] Логирование (console + RotatingFileHandler)
- [x] Seed data (management command seed_data)

---

## Бекнур

### Фаза 1
- [ ] Structured logging middleware — JSON формат, request method, path, status code, duration
  - Файлы: `apps/abstract/middleware.py`, `settings/base.py`
- [ ] Signal handler — `post_save` на Article, audit log (кто, что, когда изменил)
  - Файлы: `apps/main/signals.py`, `apps/main/apps.py`
- [ ] Custom data migration — нормализация slug полей / существующих данных
  - Файлы: `apps/main/migrations/0002_*.py`
- [ ] EXPLAIN анализ запросов + добавить индексы (author, category, created_at)
  - Файлы: `apps/main/models.py`

### Фаза 2
- [ ] Стандартизированный error format — custom exception handler для DRF
  - Файлы: `apps/abstract/exceptions.py`, `settings/base.py`
- [ ] Health check endpoint `/api/health/`
  - Файлы: `settings/urls.py`, новый view
- [ ] Тесты для middleware, signals, error handler
  - Файлы: `apps/main/tests/test_middleware.py`, `test_signals.py`

---

## Турарбек

### Фаза 1
- [ ] Celery конфигурация — app, config, Redis как broker
  - Файлы: `settings/celery.py`, `settings/__init__.py`
- [ ] On-demand Celery task — email при регистрации + обработка данных
  - Файлы: `apps/accounts/tasks.py`, `apps/main/tasks.py`
- [ ] Periodic Celery task — очистка soft-deleted записей / сбор статистики
  - Файлы: `apps/abstract/tasks.py`

### Фаза 2
- [ ] Retry logic с exponential backoff + idempotent task design
  - Файлы: tasks.py
- [ ] DRF Throttling — IP-based (100/hr анонимы) + User-based (1000/hr)
  - Файлы: `settings/base.py`, `apps/abstract/throttles.py`
- [ ] Custom rate limit для login (5/min), register (10/hr)
  - Файлы: `apps/accounts/auth/views.py`
- [ ] Docker-compose: добавить Redis + Celery worker + Celery beat
  - Файлы: `docker-compose.yml`
- [ ] Тесты для Celery tasks + rate limiting
  - Файлы: `tests/test_tasks.py`, `test_throttle.py`

---

## Азат

### Фаза 1
- [ ] Django Channels установка + ASGI routing config
  - Файлы: `settings/asgi.py`, `settings/base.py`, `pyproject.toml`
- [ ] WebSocket consumer — echo + welcome message при подключении
  - Файлы: `apps/main/consumers.py`, `apps/main/routing.py`
- [ ] Real-time notifications — broadcast при создании Article/Comment через channel layer
  - Файлы: `apps/main/consumers.py`, signals integration

### Фаза 2
- [ ] i18n: LocaleMiddleware + LANGUAGES config + Accept-Language header
  - Файлы: `settings/base.py`
- [ ] Файлы переводов (.po/.mo) для kk, ru, en + локализация динамических ответов
  - Файлы: `locale/*/LC_MESSAGES/django.po`
- [ ] Локализация email шаблона на 2 языка
  - Файлы: `templates/emails/`
- [ ] Nginx config — reverse proxy, static/media, WebSocket upgrade headers
  - Файлы: `nginx/nginx.conf`
- [ ] SSL/TLS (self-signed для dev)
  - Файлы: `nginx/ssl/`

### Фаза 3
- [ ] Docker-compose: добавить Nginx + Daphne (ASGI server)
  - Файлы: `docker-compose.yml`, `dockerfiles/`
- [ ] Тесты для WebSocket consumers + i18n
  - Файлы: `tests/test_ws.py`, `test_i18n.py`

---

## Бекзат

### Фаза 1
- [ ] Redis caching — cache backend + кеширование статей с TTL + инвалидация при update/delete
  - Файлы: `settings/base.py`, `apps/main/views.py`

### Redis caching — notes

- **Keys:**
  - Detail: `article:detail:<id>`
  - List: `article:list:v<version>:<short-hash>` (includes atomic list version)
- **TTLs:**
  - `ARTICLE_DETAIL_TTL` (env, default 300s)
  - `ARTICLE_LIST_TTL` (env, default 60s)
- **Invalidation:** `post_save`/`post_delete` on `Article` deletes detail key and `INCR` list version.
- **Files:** `apps/main/utils/cache.py`, `apps/main/signals.py`, `apps/main/views.py`, `settings/base.py`
- [ ] Async endpoint — aiohttp fetch внешнего API + обработка + кеш
  - Файлы: `apps/main/views.py`

### Фаза 2
- [ ] GitHub Actions CI/CD — lint, pytest, docker build
  - Файлы: `.github/workflows/ci.yml`
- [ ] Sentry интеграция — error tracking
  - Файлы: `settings/base.py`, `pyproject.toml`
- [ ] Prometheus metrics + health check
  - Файлы: `settings/base.py`
- [ ] Structured logging (python-json-logger / structlog) — апгрейд существующего логирования
  - Файлы: `settings/base.py`

### Фаза 3
- [ ] Dockerfile optimize — multi-stage build
  - Файлы: `dockerfiles/backend.Dockerfile`
- [ ] Тесты для кеширования + async endpoint
  - Файлы: `tests/test_cache.py`, `test_async.py`

---

## Зависимости

```
Турарбек (Redis + Celery docker) → Бекзат (Redis cache)
Бекнур (Signal handlers)         → Азат (real-time broadcast через signals)
Азат (Channels config)           → Азат (Nginx WebSocket upgrade)
Турарбек (Celery config)         → Турарбек (Docker Celery services)
```

---

## Новые зависимости (pyproject.toml)

```toml
redis>=5.0.0
django-redis>=5.4.0
celery>=5.4.0
channels>=4.1.0
channels-redis>=4.2.0
daphne>=4.1.0
python-json-logger>=3.0.0
aiohttp>=3.9.0
sentry-sdk>=2.0.0
django-prometheus>=2.3.0
```

---

## Чеклист перед сдачей

- [ ] `docker-compose up` — все сервисы (Django/Daphne, Postgres, Redis, Celery worker, Celery beat, Nginx)
- [ ] `pytest` — все тесты зелёные
- [ ] `/api/docs/` через Nginx — Swagger работает
- [ ] `ws://localhost/ws/notifications/` — WebSocket подключение, echo, welcome
- [ ] Создать статью → broadcast клиентам через WebSocket
- [ ] `Accept-Language: kk` → ответы на казахском
- [ ] Повторный `GET /api/articles/` — из Redis кеша
- [ ] Превысить лимит запросов → 429 Too Many Requests
- [ ] `git push` → GitHub Actions pipeline зелёный
- [ ] Sentry — тестовая ошибка видна
- [ ] `/api/health/` → 200 OK
- [ ] Регистрация → Celery email task в очереди
