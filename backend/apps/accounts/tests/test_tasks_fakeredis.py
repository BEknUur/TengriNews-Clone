import pytest

from django.core.cache import cache

from apps.accounts.tests.factories import UserFactory
from apps.accounts.tasks import send_welcome_email_task


@pytest.mark.django_db
def test_send_welcome_email_locking(monkeypatch):
    user = UserFactory()

  
    monkeypatch.setattr(cache, "add", lambda k, v, timeout=None: False)
    res = send_welcome_email_task.apply(args=[user.id])
    assert (
        "already running" in res.get() or "already been sent" in res.get()
    )


@pytest.mark.django_db
def test_send_welcome_email_sets_done_key(monkeypatch):
    user = UserFactory()
    
    monkeypatch.setattr("apps.accounts.tasks.render_to_string", lambda t, ctx: "x")
    monkeypatch.setattr("apps.accounts.tasks.send_mail", lambda **kwargs: 1)
    cache.clear()
    res = send_welcome_email_task.apply(args=[user.id])
    
    assert "Welcome email" in res.get()
    assert cache.get(f"welcome_email_sent_{user.id}") is not None
