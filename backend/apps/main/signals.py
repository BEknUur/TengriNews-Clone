"""Signal handlers for article and comment creation events."""

from __future__ import annotations

from typing import Any

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

from apps.abstracts.middleware import get_current_user
from apps.main.models import Article, ArticleAuditLog, Comment
from apps.main.realtime import broadcast_article_created, broadcast_comment_created
from apps.main.utils.cache import (
    make_article_detail_key,
    cache_delete,
    incr_list_version,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def notify_article_created(
    sender: type[Article],
    instance: Article,
    created: bool,
    **kwargs: dict[str, Any],
) -> None:
    if created:
        broadcast_article_created(instance)


@receiver(post_save, sender=Comment)
def notify_comment_created(
    sender: type[Comment],
    instance: Comment,
    created: bool,
    **kwargs: dict[str, Any],
) -> None:
    if created:
        broadcast_comment_created(instance)


def build_article_snapshot(article: Article) -> dict[str, object]:
    """Build compact audit snapshot for Article."""
    return {
        "id": article.pk,
        "title": article.title,
        "slug": article.slug,
        "author_id": article.author_id,
        "category_id": article.category_id,
        "is_published": article.is_published,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "view_count": article.view_count,
    }


@receiver(post_save, sender=Article)
def write_article_audit_log(
    sender: type[Article],
    instance: Article,
    created: bool,
    **kwargs: dict[str, Any],
) -> None:
    """Create audit log after Article create/update."""
    ArticleAuditLog.objects.create(
        article=instance,
        actor=get_current_user(),
        action=ArticleAuditLog.Action.CREATED
        if created
        else ArticleAuditLog.Action.UPDATED,
        snapshot=build_article_snapshot(instance),
    )


@receiver(post_save, sender=Article)
def invalidate_article_cache_on_save(
    sender: type[Article], instance: Article, created: bool, **kwargs: dict[str, Any]
) -> None:
    """Invalidate article caches after create/update."""
    try:
        key = make_article_detail_key(instance.pk)
        cache_delete(key)
    except Exception:  # pragma: no cover - defensive
        logger.exception("failed to delete article detail cache")

    try:
        incr_list_version()
    except Exception:  # pragma: no cover - defensive
        logger.exception("failed to bump article list version")


@receiver(post_delete, sender=Article)
def invalidate_article_cache_on_delete(
    sender: type[Article], instance: Article, **kwargs: dict[str, Any]
) -> None:
    """Invalidate caches after delete."""
    try:
        key = make_article_detail_key(instance.pk)
        cache_delete(key)
    except Exception:  # pragma: no cover - defensive
        logger.exception("failed to delete article detail cache on delete")

    try:
        incr_list_version()
    except Exception:  # pragma: no cover - defensive
        logger.exception("failed to bump article list version on delete")
