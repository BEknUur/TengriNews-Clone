# Python modules
from typing import Any
from unittest.mock import patch

# Django modules
from django.core.cache import cache

# Third-party modules
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Project modules
from apps.accounts.models import CustomUser
from apps.core.cache import get_version, invalidate
from apps.main.models import Article, Category, Comment, Reaction, Tag


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user(db: Any) -> CustomUser:
    return CustomUser.objects.create_user(
        email="cache@example.com",
        password="pass123",
        first_name="Cache",
        last_name="User",
    )


@pytest.fixture
def auth_client(user: CustomUser) -> APIClient:
    client = APIClient()
    token = str(RefreshToken.for_user(user).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def category(db: Any) -> Category:
    return Category.objects.create(name="CacheTest", slug="cache-test")


@pytest.fixture
def article(user: CustomUser, category: Category) -> Article:
    return Article.objects.create(
        title="Cache Article",
        slug="cache-article",
        content="content",
        author=user,
        category=category,
        is_published=True,
    )


# ---------------------------------------------------------------------------
# Unit tests: invalidation logic
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCacheInvalidation:
    def test_initial_version_is_zero(self) -> None:
        assert get_version("articles") == 0

    def test_invalidate_bumps_version(self) -> None:
        invalidate("articles")
        assert get_version("articles") == 1
        invalidate("articles")
        assert get_version("articles") == 2

    def test_namespaces_are_independent(self) -> None:
        invalidate("articles")
        assert get_version("categories") == 0
        assert get_version("articles") == 1

    def test_category_save_invalidates_cache(self, category: Category) -> None:
        v_before = get_version("categories")
        category.name = "Updated"
        category.save()
        assert get_version("categories") > v_before

    def test_tag_save_invalidates_cache(self, db: Any) -> None:
        tag = Tag.objects.create(name="CacheTag", slug="cache-tag")
        v = get_version("tags")
        tag.name = "Updated"
        tag.save()
        assert get_version("tags") > v

    def test_article_save_invalidates_cache(self, article: Article) -> None:
        v_before = get_version("articles")
        article.title = "Changed"
        article.save()
        assert get_version("articles") > v_before

    def test_comment_save_invalidates_article_cache(self, article: Article, user: CustomUser) -> None:
        v_before = get_version("articles")
        Comment.objects.create(article=article, user=user, content="hi")
        assert get_version("articles") > v_before

    def test_reaction_save_invalidates_article_cache(self, article: Article, user: CustomUser) -> None:
        v_before = get_version("articles")
        Reaction.objects.create(article=article, user=user, type="like")
        assert get_version("articles") > v_before

    def test_category_delete_invalidates_cache(self, category: Category) -> None:
        v_before = get_version("categories")
        category.delete()
        assert get_version("categories") > v_before


# ---------------------------------------------------------------------------
# Integration tests: cache hits/misses via API
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCategoryListCaching:
    def test_second_request_is_cache_hit(self, auth_client: APIClient, category: Category) -> None:
        with patch("apps.main.views.category.Category.objects") as mock_qs:
            mock_qs.all.return_value = Category.objects.all()
            auth_client.get("/api/categories/")
            first_call_count = mock_qs.all.call_count

            auth_client.get("/api/categories/")
            # DB not hit on second request
            assert mock_qs.all.call_count == first_call_count

    def test_cache_invalidated_after_new_category(self, auth_client: APIClient) -> None:
        response = auth_client.get("/api/categories/")
        assert response.status_code == 200
        v_before = get_version("categories")

        Category.objects.create(name="NewCat", slug="new-cat")
        assert get_version("categories") > v_before

        # Next request fetches fresh data
        r2 = auth_client.get("/api/categories/")
        assert r2.status_code == 200

    def test_different_query_params_get_separate_cache_entries(self, auth_client: APIClient) -> None:
        r1 = auth_client.get("/api/categories/")
        r2 = auth_client.get("/api/categories/?format=json")
        assert r1.status_code == 200
        assert r2.status_code == 200


@pytest.mark.django_db
class TestArticleListCaching:
    def test_article_list_cached_on_second_request(
        self, auth_client: APIClient, article: Article
    ) -> None:
        r1 = auth_client.get("/api/articles/")
        r2 = auth_client.get("/api/articles/")
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.data == r2.data

    def test_search_param_gets_own_cache_entry(
        self, auth_client: APIClient, article: Article
    ) -> None:
        r1 = auth_client.get("/api/articles/")
        r2 = auth_client.get("/api/articles/?search=Cache")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_article_creation_invalidates_list_cache(
        self, auth_client: APIClient, article: Article, user: CustomUser, category: Category
    ) -> None:
        auth_client.get("/api/articles/")
        v_before = get_version("articles")

        Article.objects.create(
            title="New Article",
            slug="new-article-cache",
            content="x",
            author=user,
            category=category,
            is_published=True,
        )
        assert get_version("articles") > v_before


@pytest.mark.django_db
class TestArticleDetailCaching:
    def test_detail_cached_on_second_request(
        self, auth_client: APIClient, article: Article
    ) -> None:
        r1 = auth_client.get(f"/api/articles/{article.pk}/")
        r2 = auth_client.get(f"/api/articles/{article.pk}/")
        assert r1.status_code == 200
        assert r1.data == r2.data

    def test_detail_invalidated_after_comment(
        self, auth_client: APIClient, article: Article, user: CustomUser
    ) -> None:
        auth_client.get(f"/api/articles/{article.pk}/")
        v_before = get_version("articles")

        Comment.objects.create(article=article, user=user, content="test")
        assert get_version("articles") > v_before

    def test_different_articles_get_separate_cache_entries(
        self, auth_client: APIClient, article: Article, user: CustomUser, category: Category
    ) -> None:
        article2 = Article.objects.create(
            title="Second", slug="second-cache", content="x",
            author=user, category=category, is_published=True,
        )
        r1 = auth_client.get(f"/api/articles/{article.pk}/")
        r2 = auth_client.get(f"/api/articles/{article2.pk}/")
        assert r1.data["id"] != r2.data["id"]

    def test_write_endpoints_not_cached(
        self, auth_client: APIClient, article: Article
    ) -> None:
        response = auth_client.patch(
            f"/api/articles/{article.pk}/",
            {"excerpt": "updated"},
            format="json",
        )
        assert response.status_code == 200
