import pytest

from django.db import transaction


@pytest.mark.django_db
def test_register_triggers_welcome_email(monkeypatch, api_client):
    called = {"delay": False}

    def fake_delay(uid):
        called["delay"] = True

    # monkeypatch the delay method used in register view
    monkeypatch.setattr("apps.accounts.views.auth.send_welcome_email_task.delay", fake_delay)

    # ensure on_commit calls immediately in tests
    monkeypatch.setattr("apps.accounts.views.auth.transaction.on_commit", lambda fn: fn())

    payload = {
        "email": "integ@example.test",
        "password": "strongpass123",
        "password_confirm": "strongpass123",
        "first_name": "I",
        "last_name": "T",
    }
    resp = api_client.post("/api/accounts/auth/register/", payload)
    assert resp.status_code == 201
    assert called["delay"] is True
