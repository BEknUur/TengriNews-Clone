# Проект TengriNews Clone (AngryNews)

План разработки: 8 моделей данных и ~20 эндпоинтов.

## 1. Модели данных (8 моделей)

- [ ] **User (Custom User Model)**
    - Поля: `id`, `email` (unique), `password`, `full_name`, `role` (USER/EDITOR/ADMIN), `is_active`, `is_staff`, `created_at`.
- [ ] **Category (Категории)**
    - Поля: `name`, `slug` (unique), `is_active`.
- [ ] **Tag (Теги)**
    - Поля: `name`, `slug` (unique).
- [ ] **Article (Статьи)**
    - Поля: `title`, `slug` (unique), `preview_text`, `content`, `cover_image`, `category` (FK), `tags` (M2M), `author` (FK User), `status` (DRAFT/PUBLISHED), `published_at`, `views_count`, `created_at`, `updated_at`.
- [ ] **Comment (Комментарии)**
    - Поля: `article` (FK), `user` (FK), `text`, `is_hidden`, `created_at`, `updated_at`.
- [ ] **Reaction (Лайки)**
    - Поля: `user` (FK), `article` (FK), `type` (LIKE), `created_at`.
    - Уникальность: (user, article).
- [ ] **Bookmark (Закладки)**
    - Поля: `user` (FK), `article` (FK), `created_at`.
    - Уникальность: (user, article).
- [ ] **Media (Медиафайлы)**
    - Поля: `file/url`, `type` (IMAGE), `uploaded_by` (FK User), `created_at`.

---

## 2. API Endpoints (~20 эндпоинтов)

### Auth & Users
- [ ] `POST /api/auth/register/` — Регистрация.
- [ ] `POST /api/auth/login/` — Получение JWT.
- [ ] `POST /api/auth/refresh/` — Обновление токена.
- [ ] `GET /api/users/me/` — Мой профиль.
- [ ] `PATCH /api/users/me/` — Редактирование профиля.
- [ ] `GET /api/users/` — Список пользователей (Admin only).

### Categories & Tags
- [ ] `GET /api/categories/` — Список категорий.
- [ ] `GET /api/categories/{slug}/` — Детали категории.
- [ ] `GET /api/tags/` — Список тегов.
- [ ] `GET /api/tags/{slug}/` — Детали тега.

### Articles
- [ ] `GET /api/articles/` — Список статей (Фильтры: `category`, `tag`, `author`, `status=PUBLISHED`, `search`, `ordering=-published_at`).
- [ ] `GET /api/articles/{slug}/` — Деталка статьи.
- [ ] `POST /api/articles/` — Создание (Editor/Admin).
- [ ] `PATCH /api/articles/{slug}/` — Редактирование (Author/Editor/Admin).
- [ ] `DELETE /api/articles/{slug}/` — Удаление (Admin).
- [ ] `POST /api/articles/{slug}/publish/` — Опубликовать.
- [ ] `POST /api/articles/{slug}/view/` — Засчитать просмотр.

### Comments, Reactions & Bookmarks
- [ ] `GET /api/articles/{slug}/comments/` — Комментарии к статье.
- [ ] `POST /api/articles/{slug}/comments/` — Добавить коммент (Auth).
- [ ] `DELETE /api/comments/{id}/` — Удалить коммент (Author/Admin).
- [ ] `POST /api/articles/{slug}/like/` — Поставить/убрать лайк.
- [ ] `POST /api/articles/{slug}/bookmark/` — Добавить/убрать закладку.
- [ ] `GET /api/bookmarks/` — Мои закладки.

### Media
- [ ] `POST /api/media/upload/` — Загрузка файла.
- [ ] `GET /api/media/` — Список файлов (Admin/Editor).

---

## 3. Технический стек и инфраструктура

### Докеризация
- [ ] `Dockerfile` для Django.
- [ ] `Dockerfile` для React (Multi-stage build).
- [ ] `docker-compose.yml` (App, DB, Redis, Celery).

### Frontend (React + Vite)
- [ ] Инициализация проекта на React + Vite + TypeScript.
- [ ] Настройка Axios для работы с API.
- [ ] Базовая верстка: Главная страница (список статей), Детальная страница статьи, Авторизация.

### Документация и Инструменты
- [ ] **Swagger/drf-spectacular**: Полная документация всех эндпоинтов.
- [ ] **Redis**: Кэширование тяжелых запросов (например, список популярных статей).
- [ ] **Logging**: Настройка логирования ошибок и важных событий в Django.

### Скрипты
- [ ] `make dev` или скрипт для быстрого запуска проекта.
- [ ] Скрипт для заполнения базы тестовыми данными (seed script).

---

## 4. Тестирование

- [ ] Unit-тесты для моделей.
- [ ] Integration-тесты для основных API эндпоинтов (Auth, Article CRUD).
- [ ] Тесты для логики разрешений (Permissions).

---

## 5. Permissions (Права доступа)

- [ ] **Статьи**: Читают все. Создают EDITOR/ADMIN. Редактируют только авторы или редакторы. Удаляют только админы.
- [ ] **Комментарии**: Пишут только авторизованные. Удаляют авторы или админы.
- [ ] **Закладки/Лайки**: Только для авторизованных.
- [ ] **Профиль**: Каждый правит только свой.