# Python modules
from typing import Any

# Django modules
from django.utils import timezone

# Third-party modules
import pytest

# Project modules
from apps.accounts.models import CustomUser
from apps.main.models import Article, Category
from apps.main.tasks import process_article_content_task


@pytest.fixture
def user(db: Any) -> CustomUser:
    return CustomUser.objects.create_user(
        email="task@example.com",
        password="pass123",
        first_name="Task",
        last_name="User",
    )


@pytest.fixture
def category(db: Any) -> Category:
    return Category.objects.create(name="TaskCat", slug="task-cat-main")


@pytest.fixture
def article(user: CustomUser, category: Category) -> Article:
    return Article.objects.create(
        title="Test",
        slug="test-task-article",
        content="word " * 200,
        author=user,
        category=category,
    )


@pytest.mark.django_db
class TestProcessArticleContentTask:
    def test_raises_for_nonexistent_article(self, db: Any) -> None:
        with pytest.raises(ValueError, match="does not exist"):
            process_article_content_task._orig_run(article_id=99999)

    def test_returns_correct_word_count(self, article: Article) -> None:
        result = process_article_content_task.apply(args=[article.pk])
        data = result.get()

        assert data["article_id"] == article.pk
        assert data["word_count"] == 200

    def test_read_time_200_words_is_1_minute(self, article: Article) -> None:
        result = process_article_content_task.apply(args=[article.pk])
        assert result.get()["read_time_minutes"] == 1

    def test_read_time_400_words_is_2_minutes(self, user: CustomUser, category: Category) -> None:
        long_article = Article.objects.create(
            title="Long",
            slug="long-article",
            content="word " * 400,
            author=user,
            category=category,
        )
        result = process_article_content_task.apply(args=[long_article.pk])
        assert result.get()["read_time_minutes"] == 2

    def test_empty_content_returns_zero_read_time(self, user: CustomUser, category: Category) -> None:
        empty_article = Article.objects.create(
            title="Empty",
            slug="empty-article",
            content="",
            author=user,
            category=category,
        )
        result = process_article_content_task.apply(args=[empty_article.pk])
        data = result.get()

        assert data["word_count"] == 0
        assert data["read_time_minutes"] == 0

    def test_strips_html_tags_before_counting(self, user: CustomUser, category: Category) -> None:
        html_article = Article.objects.create(
            title="HTML",
            slug="html-article",
            content="<p>one</p> <b>two</b> <i>three</i>",
            author=user,
            category=category,
        )
        result = process_article_content_task.apply(args=[html_article.pk])
        assert result.get()["word_count"] == 3

    def test_ignores_soft_deleted_article(self, article: Article) -> None:
        Article.objects.filter(pk=article.pk).update(deleted_at=timezone.now())
        with pytest.raises(ValueError, match="does not exist"):
            process_article_content_task._orig_run(article_id=article.pk)
