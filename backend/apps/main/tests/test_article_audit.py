# Python modules
from typing import Any

# Third-party modules
import pytest

# Project modules
from apps.main.models import Article, ArticleAuditLog


@pytest.mark.django_db
def test_article_create_writes_audit_log(user: Any, category: Any) -> None:
    """Test `test_article_create_writes_audit_log`."""
    article = Article.objects.create(
        title="Audit Article",
        slug="audit-article",
        content="Audit content",
        author=user,
        category=category,
        is_published=True,
    )

    audit_log = ArticleAuditLog.objects.get(
        article=article,
        action=ArticleAuditLog.Action.CREATED,
    )
    assert audit_log.snapshot["title"] == "Audit Article"
    assert audit_log.snapshot["author_id"] == user.id


@pytest.mark.django_db
def test_article_update_writes_audit_log(article: Any) -> None:
    """Test `test_article_update_writes_audit_log`."""
    article.title = "Updated Audit Title"
    article.save(update_fields=["title"])

    assert ArticleAuditLog.objects.filter(
        article=article,
        action=ArticleAuditLog.Action.UPDATED,
        snapshot__title="Updated Audit Title",
    ).exists()
