import pytest

from django.core import mail

from apps.accounts.tests.factories import UserFactory
from apps.accounts.tasks import send_welcome_email_task


@pytest.mark.django_db
def test_send_welcome_email_task_sends_and_sets_cache(monkeypatch, settings):
    user = UserFactory()

    # stub render_to_string and send_mail
    monkeypatch.setattr("apps.accounts.tasks.render_to_string", lambda t, ctx: "content")
    monkeypatch.setattr("apps.accounts.tasks.send_mail", lambda **kwargs: 1)

    # ensure cache is clear
    from django.core.cache import cache

    cache.clear()

    res = send_welcome_email_task.apply(args=[user.id])
    # `apply` returns an EagerResult; call `.get()` to obtain the task return value
    assert "Welcome email" in res.get()


@pytest.mark.django_db
def test_send_welcome_email_task_handles_missing_user():
    # call the underlying function directly to avoid Celery's retry wrapper
    with pytest.raises(ValueError):
        send_welcome_email_task._orig_run(user_id=999999)
# Python modules
from typing import Any
from unittest.mock import patch

# Django modules
from django.core.cache import cache

# Third-party modules
import pytest

# Project modules
from apps.accounts.models import CustomUser
from apps.accounts.tasks import send_welcome_email_task


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Clear cache before each test to prevent state bleed between tests."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user(db: Any) -> CustomUser:
    return CustomUser.objects.create_user(
        email="welcome@example.com",
        password="pass123",
        first_name="Welcome",
        last_name="User",
    )


@pytest.mark.django_db
class TestSendWelcomeEmailTask:
    def test_sends_email_for_existing_user(self, user: CustomUser) -> None:
        with patch("apps.accounts.tasks.send_mail") as mock_send:
            result = send_welcome_email_task.apply(args=[user.pk])

        assert mock_send.called
        _, kwargs = mock_send.call_args
        assert user.email in kwargs["recipient_list"]
        assert "sent" in result.get()

    def test_raises_value_error_for_nonexistent_user(self, db: Any) -> None:
        with pytest.raises(ValueError, match="does not exist"):
            send_welcome_email_task._orig_run(user_id=99999)

    def test_idempotent_second_call_skipped(self, user: CustomUser) -> None:
        with patch("apps.accounts.tasks.send_mail"):
            send_welcome_email_task.apply(args=[user.pk])

        with patch("apps.accounts.tasks.send_mail") as mock_second:
            result = send_welcome_email_task.apply(args=[user.pk])

        mock_second.assert_not_called()
        assert "already been sent" in result.get()

    def test_email_subject_contains_user_first_name(self, user: CustomUser) -> None:
        with patch("apps.accounts.tasks.send_mail") as mock_send:
            send_welcome_email_task.apply(args=[user.pk])

        assert mock_send.called
        _, kwargs = mock_send.call_args
        assert user.first_name in kwargs["subject"]

    def test_lock_prevents_concurrent_execution(self, user: CustomUser) -> None:
        lock_key = f"welcome_email_lock_{user.pk}"
        cache.set(lock_key, "1", timeout=300)

        with patch("apps.accounts.tasks.send_mail") as mock_send:
            result = send_welcome_email_task.apply(args=[user.pk])

        mock_send.assert_not_called()
        assert "already running" in result.get()
