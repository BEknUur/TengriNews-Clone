# Python modules
from typing import Any

# Django modules
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import override, gettext as _

# Third-party modules
from celery import shared_task

# Project modules
from apps.accounts.models import CustomUser


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=5,
)
def send_welcome_email_task(self: Any, user_id: int) -> str | Exception:
    """Execute send welcome email task logic and return its result."""
    user: CustomUser = CustomUser.objects.filter(
        id=user_id, deleted_at__isnull=True
    ).first()
    if not user:
        raise ValueError(f"User with id {user_id} does not exist.")
    done_key = f"welcome_email_sent_{user_id}"
    lock_key = f"welcome_email_lock_{user_id}"

    if cache.get(done_key):
        return f"Welcome email for user {user_id} has already been sent."

    if not cache.add(lock_key, "1", timeout=300):
        return f"Task for user {user_id} is already running."
    try:
        user_lang = getattr(user, "preferred_language", None) or "en"
        with override(user_lang):
            subject = render_to_string(
                "emails/welcome/subject.txt", {"user": user}
            ).strip()
            message = render_to_string("emails/welcome/body.txt", {"user": user})

        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@tengrinews.kz"),
            recipient_list=[user.email],
        )
        cache.set(done_key, "1", timeout=60 * 60 * 24)
        return _("Welcome email for user %(user_id)s has been sent.") % {
            "user_id": user_id
        }
    except Exception as e:
        raise e
    finally:
        cache.delete(lock_key)
