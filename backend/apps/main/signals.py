"""Signal handlers for article and comment creation events."""

from __future__ import annotations

from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.main.models import Article, Comment
from apps.main.realtime import broadcast_article_created, broadcast_comment_created


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