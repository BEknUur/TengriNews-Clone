from __future__ import annotations

# Python modules
import logging
from typing import Any

# Django modules
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

# Project modules
from apps.core.cache import invalidate
from apps.core.middleware import get_current_user
from apps.main.models import Article, ArticleAuditLog, Category, Comment, Reaction, Tag
from apps.main.realtime import broadcast_article_created, broadcast_comment_created

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_category_cache(sender: type[Category], **kwargs: Any) -> None:
    invalidate("categories")


@receiver(post_save, sender=Tag)
@receiver(post_delete, sender=Tag)
def invalidate_tag_cache(sender: type[Tag], **kwargs: Any) -> None:
    invalidate("tags")


@receiver(post_save, sender=Article)
@receiver(post_delete, sender=Article)
def invalidate_article_cache(sender: type[Article], instance: Article, **kwargs: Any) -> None:
    invalidate("articles")


@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def invalidate_article_cache_on_comment(sender: type[Comment], instance: Comment, **kwargs: Any) -> None:
    invalidate("articles")


@receiver(post_save, sender=Reaction)
@receiver(post_delete, sender=Reaction)
def invalidate_article_cache_on_reaction(sender: type[Reaction], instance: Reaction, **kwargs: Any) -> None:
    invalidate("articles")


@receiver(post_save, sender=Article)
def notify_article_created(
    sender: type[Article],
    instance: Article,
    created: bool,
    **kwargs: Any,
) -> None:
    """Broadcast WebSocket event when a new article is published."""
    if created:
        logger.debug("Broadcasting article_created event: id=%s", instance.pk)
        broadcast_article_created(instance)


@receiver(post_save, sender=Comment)
def notify_comment_created(
    sender: type[Comment],
    instance: Comment,
    created: bool,
    **kwargs: Any,
) -> None:
    """Broadcast WebSocket event when a new comment is posted."""
    if created:
        logger.debug("Broadcasting comment_created event: id=%s article_id=%s", instance.pk, instance.article_id)
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
    **kwargs: Any,
) -> None:
    """Create audit log after Article create/update."""
    action = ArticleAuditLog.Action.CREATED if created else ArticleAuditLog.Action.UPDATED
    ArticleAuditLog.objects.create(
        article=instance,
        actor=get_current_user(),
        action=action,
        snapshot=build_article_snapshot(instance),
    )
    logger.debug("Audit log written: article_id=%s action=%s", instance.pk, action)
