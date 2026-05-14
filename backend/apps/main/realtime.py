"""Helpers for broadcasting news events over Channels."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

if TYPE_CHECKING:
    from apps.main.models import Article, Comment

logger = logging.getLogger(__name__)

NEWS_GROUP_NAME = "news_notifications"


def _broadcast(event_type: str, payload: dict[str, Any]) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    try:
        async_to_sync(channel_layer.group_send)(
            NEWS_GROUP_NAME,
            {
                "type": event_type,
                "payload": payload,
            },
        )
    except Exception:
        logger.exception("Failed to broadcast %s event.", event_type)


def _user_payload(user: Any) -> dict[str, Any] | None:
    if user is None:
        return None
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


def broadcast_article_created(article: "Article") -> None:  # noqa: F821
    """Broadcast an article creation event."""
    _broadcast(
        "article_created",
        {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "excerpt": article.excerpt,
            "content": article.content,
            "author": _user_payload(article.author),
            "category": {
                "id": article.category_id,
                "name": article.category.name,
                "slug": article.category.slug,
            }
            if article.category
            else None,
            "is_published": article.is_published,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "created_at": article.created_at.isoformat() if article.created_at else None,
        },
    )


def broadcast_comment_created(comment: "Comment") -> None:  # noqa: F821
    """Broadcast a comment creation event."""
    _broadcast(
        "comment_created",
        {
            "id": comment.id,
            "article": comment.article_id,
            "parent": comment.parent_id,
            "content": comment.content,
            "is_active": comment.is_active,
            "user": _user_payload(comment.user),
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
        },
    )