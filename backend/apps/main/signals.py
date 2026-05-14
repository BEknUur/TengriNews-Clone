from __future__ import annotations

# Python modules
from typing import Any

# Django modules
from django.db.models.signals import post_save
from django.dispatch import receiver

# Project modules
from apps.core.middleware import get_current_user
from apps.main.models import Article, ArticleAuditLog, Comment
from apps.main.realtime import broadcast_article_created, broadcast_comment_created


@receiver(post_save, sender=Article)
def notify_article_created(
    sender: type[Article],
    instance: Article,
    created: bool,
    **kwargs: dict[str, Any],
) -> None:
    """Execute notify article created logic and return its result."""
    if created:
        broadcast_article_created(instance)


@receiver(post_save, sender=Comment)
def notify_comment_created(
    sender: type[Comment],
    instance: Comment,
    created: bool,
    **kwargs: dict[str, Any],
) -> None:
    """Execute notify comment created logic and return its result."""
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
