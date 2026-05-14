**What I changed**
- Added data migration `0004_normalize_slugs` to normalize and dedupe `slug` fields for `Category`, `Tag`, `Article`.
- Migration ensures transliteration with `Unidecode` (fallback if unavailable) and resolves collisions by appending `-1,-2,...`.
- Added integration tests `backend/apps/main/tests/test_migration_apply.py` to apply the migration and verify normalization, uniqueness and idempotency.
- Added `Unidecode` to `pyproject.toml` and `backend/requirements.txt`.

**Why**
Normalizes existing slugs to consistent format and allows adding unique constraints safely afterwards.

**How to test locally**
1. Backup DB (sqlite):
```bash
cp backend/localdb.sqlite3 backend/localdb.sqlite3.bak.$(date +%s)
```
2. Build backend image (to pick up deps):
```bash
docker compose build backend
```
3. Run tests:
```bash
docker compose run --rm backend pytest -q
```
4. Apply migration locally (sqlite):
```bash
docker compose run --rm backend python manage.py migrate main
```
5. (Optional) Apply to Postgres (staging):
```bash
docker compose exec -T postgres pg_dump -U myuser -d mydatabase -Fc > /tmp/backup-$(date +%F-%s).dump
docker compose run --rm -e TENGRI_ENV_ID=prod backend python manage.py migrate main
```

**Verification SQL examples**
```sql
-- find duplicate slugs
SELECT slug, COUNT(*) FROM main_article GROUP BY slug HAVING COUNT(*)>1;
-- find empty slugs
SELECT COUNT(*) FROM main_article WHERE slug IS NULL OR trim(slug)='';
```

**Rollback plan**
- Restore DB from backup created before running migration.

**Notes for reviewer**
- Migration `backwards` is intentionally a no-op; restoring previous values requires DB restore.
- Logging uses module logger; logged messages will be available via project logging configuration.
