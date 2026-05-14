# Python modules
from datetime import timedelta
from logging import getLogger
from typing import Any

# Django modules
from django.utils import timezone

# Third-party modules
from celery import shared_task

# Project modules
from apps.accounts.models import CustomUser
from apps.main.models import Article, Category, Comment, Reaction, Tag

logger = getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
)
def cleanup_soft_deleted_records(
    self: Any,
    retention_days: int = 30,
) -> str | Exception:
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    deleted_count = {}
    models_to_cleanup = [
        ("users", CustomUser),
        ("articles", Article),
        ("categories", Category),
        ("tags", Tag),
        ("comments", Comment),
        ("reactions", Reaction),
    ]
    for model_name, model in models_to_cleanup:
        qs = model.objects.filter(deleted_at__lt=cutoff_date)
        count = qs.count()
        qs.delete()
        deleted_count[model_name] = count
    logger.info(f"Soft-deleted records cleanup completed: {deleted_count}")
    return f"Soft-deleted records cleanup completed: {deleted_count}"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
)
def collect_content_statistics(self: Any) -> dict[str, int]:
    stats = {
        "users_total": CustomUser.objects.filter(deleted_at__isnull=True).count(),
        "total_articles": Article.objects.filter(deleted_at__isnull=True).count(),
        "articles_published": Article.objects.filter(
            deleted_at__isnull=True, published_at=True
        ).count(),
        "comments_total": Comment.objects.filter(deleted_at__isnull=True).count(),
        "reactions_total": Reaction.objects.filter(deleted_at__isnull=True).count(),
    }
    logger.info(f"Content statistics collected: {stats}")
    return stats
