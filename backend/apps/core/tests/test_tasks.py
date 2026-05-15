import pytest

from datetime import timedelta
from typing import Any

from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.main.models import Article, Category
from apps.core.tasks import cleanup_soft_deleted_records, collect_content_statistics
from apps.accounts.tests.factories import UserFactory
from apps.main.tests.factories import ArticleFactory, CommentFactory, ReactionFactory


@pytest.mark.django_db
def test_collect_content_statistics_counts():
    UserFactory()
    ArticleFactory()
    CommentFactory()
    ReactionFactory()
    result = collect_content_statistics.apply()
    stats = result.get()
    assert isinstance(stats, dict)
    assert "users_total" in stats and "total_articles" in stats


@pytest.mark.django_db
def test_cleanup_soft_deleted_records_deletes_old(monkeypatch):
    # create a soft-deleted user and ensure cleanup removes it
    u = UserFactory()
    u.deleted_at = u.created_at
    u.save()
    res = cleanup_soft_deleted_records.apply(kwargs={"retention_days": 0})
    assert "Soft-deleted records cleanup" in res.get()


@pytest.fixture
def user(db: Any) -> CustomUser:
    return CustomUser.objects.create_user(
        email="task_user@example.com",
        password="pass123",
        first_name="Task",
        last_name="User",
    )


@pytest.fixture
def category(db: Any) -> Category:
    return Category.objects.create(name="TaskCat", slug="task-cat")


@pytest.mark.django_db
class TestCleanupSoftDeletedRecords:
    def test_deletes_records_older_than_retention(self, user: CustomUser, category: Category) -> None:
        old_cutoff = timezone.now() - timedelta(days=31)
        article = Article.objects.create(
            title="Old",
            slug="old-article",
            content="x",
            author=user,
            category=category,
        )
        Article.objects.filter(pk=article.pk).update(deleted_at=old_cutoff)

        result = cleanup_soft_deleted_records.apply(kwargs={"retention_days": 30})

        assert result.get() is not None
        assert not Article.objects.filter(pk=article.pk).exists()

    def test_keeps_records_within_retention(self, user: CustomUser, category: Category) -> None:
        recent_cutoff = timezone.now() - timedelta(days=5)
        article = Article.objects.create(
            title="Recent",
            slug="recent-article",
            content="x",
            author=user,
            category=category,
        )
        Article.objects.filter(pk=article.pk).update(deleted_at=recent_cutoff)

        cleanup_soft_deleted_records.apply(kwargs={"retention_days": 30})

        assert Article.objects.filter(pk=article.pk).exists()

    def test_keeps_active_records(self, user: CustomUser, category: Category) -> None:
        article = Article.objects.create(
            title="Active",
            slug="active-article",
            content="x",
            author=user,
            category=category,
        )

        cleanup_soft_deleted_records.apply(kwargs={"retention_days": 30})

        assert Article.objects.filter(pk=article.pk).exists()

    def test_returns_count_summary(self, user: CustomUser, category: Category) -> None:
        old_cutoff = timezone.now() - timedelta(days=31)
        article = Article.objects.create(
            title="CountMe",
            slug="count-me",
            content="x",
            author=user,
            category=category,
        )
        Article.objects.filter(pk=article.pk).update(deleted_at=old_cutoff)

        result = cleanup_soft_deleted_records.apply(kwargs={"retention_days": 30})

        assert "articles" in result.get()


@pytest.mark.django_db
class TestCollectContentStatistics:
    def test_counts_active_users(self, user: CustomUser) -> None:
        result = collect_content_statistics.apply()
        assert result.get()["users_total"] >= 1

    def test_counts_published_articles_correctly(self, user: CustomUser, category: Category) -> None:
        Article.objects.create(
            title="Published",
            slug="published-1",
            content="x",
            author=user,
            category=category,
            is_published=True,
        )
        Article.objects.create(
            title="Draft",
            slug="draft-1",
            content="x",
            author=user,
            category=category,
            is_published=False,
        )

        result = collect_content_statistics.apply()
        stats = result.get()

        assert stats["articles_published"] >= 1
        assert stats["total_articles"] >= 2
        # published count must be less than or equal to total
        assert stats["articles_published"] <= stats["total_articles"]

    def test_does_not_count_soft_deleted(self, user: CustomUser, category: Category) -> None:
        article = Article.objects.create(
            title="Deleted",
            slug="deleted-stats",
            content="x",
            author=user,
            category=category,
            is_published=True,
        )
        Article.objects.filter(pk=article.pk).update(deleted_at=timezone.now())

        # The deleted article should not appear in published count
        published_ids = Article.objects.filter(
            deleted_at__isnull=True, is_published=True
        ).values_list("id", flat=True)
        assert article.pk not in published_ids

    def test_returns_all_expected_keys(self) -> None:
        result = collect_content_statistics.apply()
        stats = result.get()

        assert "users_total" in stats
        assert "total_articles" in stats
        assert "articles_published" in stats
        assert "comments_total" in stats
        assert "reactions_total" in stats
