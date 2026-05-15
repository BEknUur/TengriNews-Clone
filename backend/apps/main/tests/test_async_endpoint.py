import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient
import asyncio

@pytest.mark.django_db
@override_settings(
    EXTERNAL_API_URL="https://api.example.com/search",
    EXTERNAL_API_TTL=1,
)
def test_external_endpoint_cache_and_error(monkeypatch):
    client = APIClient()

    async def fake_fetch_external(url, params=None, headers=None):
        return {"id": "x", "title": "ok", "score": 1.23}

    import apps.main.utils.async_client as ac
    monkeypatch.setattr(ac, "fetch_external", fake_fetch_external)

    resp1 = client.get("/api/external/?q=hello")
    assert resp1.status_code == 200
    data1 = resp1.json()

    async def fail_fetch(*a, **kw):
        raise Exception("down")
    monkeypatch.setattr(ac, "fetch_external", fail_fetch)

    resp2 = client.get("/api/external/?q=hello")
    assert resp2.status_code == 200
    assert resp2.json() == data1