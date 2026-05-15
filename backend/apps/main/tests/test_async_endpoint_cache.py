import pytest
from django.urls import reverse
from django.test import AsyncClient, override_settings

from apps.main.views import async_endpoint as view_module
from apps.main.utils.cache import cache_get as util_cache_get

URL_NAME = 'external-data'


@pytest.fixture(autouse=True)
def clear_all_caches():
    from django.core.cache import caches
    for name in list(caches):
        try:
            caches[name].clear()
        except Exception:
            pass
    yield
    for name in list(caches):
        try:
            caches[name].clear()
        except Exception:
            pass


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        },
        "article_cache": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake-article",
        },
    }
)
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_endpoint_caches_success(monkeypatch):
    called = {"count": 0}

    async def fake_fetch(*args, **kwargs):
        called["count"] += 1
        return {"result": "ok", "value": 123}

    monkeypatch.setattr('apps.main.views.async_endpoint.fetch_external', fake_fetch)

    client = AsyncClient()
    url = reverse(URL_NAME)
    q = "test-success"

    resp1 = await client.get(url, {"q": q})
    assert resp1.status_code == 200
    assert resp1.json() == {"result": "ok", "value": 123}
    assert called["count"] == 1

    resp2 = await client.get(url, {"q": q})
    assert resp2.status_code == 200
    assert resp2.json() == {"result": "ok", "value": 123}
    assert called["count"] == 1


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake-2",
        },
        "article_cache": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake-article-2",
        },
    }
)
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_endpoint_handles_external_error_and_not_cached(monkeypatch):
    called = {"count": 0}

    async def fake_fetch_raise(*args, **kwargs):
        called["count"] += 1
        raise view_module.ExternalAPIError("external down")

    monkeypatch.setattr('apps.main.views.async_endpoint.fetch_external', fake_fetch_raise)

    client = AsyncClient()
    url = reverse(URL_NAME)
    q = "test-error"

    resp1 = await client.get(url, {"q": q})
    assert resp1.status_code == 502
    assert called["count"] == 1

    resp2 = await client.get(url, {"q": q})
    assert resp2.status_code == 502
    assert called["count"] == 2


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake-3",
        },
        "article_cache": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake-article-3",
        },
    }
)
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_cache_key_and_ttl_behavior(monkeypatch):
    async def fake_fetch(*args, **kwargs):
        return {"foo": "bar"}

    monkeypatch.setattr('apps.main.views.async_endpoint.fetch_external', fake_fetch)

    client = AsyncClient()
    url = reverse(URL_NAME)
    q = "test-ttl"

    await client.get(url, {"q": q})

    cache_key = f"external:data:q:{q}"
    cached = util_cache_get(cache_key)
    assert cached is not None
    assert cached == {"foo": "bar"}
