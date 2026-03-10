import pytest
from contextlib import nullcontext as does_not_raise
from typing import Any

from apps.main.models import Article, Category
from apps.accounts.models import CustomUser


@pytest.mark.django_db
class TestArticleViewSet:
    """Tests for ArticleViewSet endpoints."""

    def test_list_returns_200(self, auth_client) -> None:
        """GET /api/articles/ returns 200."""
        response = auth_client.get("/api/articles/")
        assert response.status_code == 200

    def test_list_has_pagination_and_data(self, auth_client, article) -> None:
        """Response contains both 'pagination' and 'data' keys."""
        response = auth_client.get("/api/articles/")
        assert "pagination" in response.data, "Must have 'pagination' key"
        assert "data" in response.data, "Must have 'data' key"

    # ─── Pagination type tests ────────────────────────────────────────────────

    def test_cursor_pagination(self, auth_client, article) -> None:
        """?pagination=cursor returns cursor-specific keys."""
        response = auth_client.get("/api/articles/?pagination=cursor")
        assert response.status_code == 200
        pagination = response.data["pagination"]
        assert "next_cursor" in pagination, "Cursor pagination must have 'next_cursor'"
        assert "ordering" in pagination, "Cursor pagination must have 'ordering'"

    def test_page_pagination(self, auth_client, article) -> None:
        """?pagination=page returns count key."""
        response = auth_client.get("/api/articles/?pagination=page")
        assert response.status_code == 200
        pagination = response.data["pagination"]
        assert "count" in pagination, "Page pagination must have 'count'"

    def test_limit_pagination(self, auth_client, article) -> None:
        """?pagination=limit returns next and previous keys."""
        response = auth_client.get("/api/articles/?pagination=limit")
        assert response.status_code == 200
        pagination = response.data["pagination"]
        assert "next" in pagination, "Limit pagination must have 'next'"
        assert "previous" in pagination, "Limit pagination must have 'previous'"

    def test_default_pagination_is_cursor(self, auth_client, article) -> None:
        """No ?pagination= param defaults to cursor format."""
        response = auth_client.get("/api/articles/")
        assert response.status_code == 200
        pagination = response.data["pagination"]
        assert "next_cursor" in pagination, "Default must be cursor pagination"

    @pytest.mark.parametrize(
        argnames=["pagination_type", "expected_key"],
        argvalues=[
            ("cursor", "next_cursor"),
            ("page", "count"),
            ("limit", "next"),
        ]
    )
    def test_all_pagination_types(
        self,
        auth_client,
        article,
        pagination_type: str,
        expected_key: str,
    ) -> None:
        """Parametrized: each pagination type returns its specific key."""
        response = auth_client.get(f"/api/articles/?pagination={pagination_type}")
        assert response.status_code == 200
        assert expected_key in response.data["pagination"], (
            f"Pagination '{pagination_type}' must contain key '{expected_key}'"
        )

    # ─── CRUD tests ───────────────────────────────────────────────────────────

    def test_retrieve_returns_200(self, auth_client, article: Article) -> None:
        """GET /api/articles/{id}/ returns 200."""
        response = auth_client.get(f"/api/articles/{article.pk}/")
        assert response.status_code == 200

    def test_retrieve_not_found(self, auth_client) -> None:
        """GET /api/articles/9999/ returns 404."""
        response = auth_client.get("/api/articles/9999/")
        assert response.status_code == 404

    def test_create_article(self, auth_client, category: Category) -> None:
        """POST /api/articles/ creates article and returns 201."""
        payload = {
            "title": "New Article",
            "slug": "new-article",
            "content": "Content here",
            "category": category.pk,
            "is_published": False,
        }
        response = auth_client.post("/api/articles/", payload)
        assert response.status_code == 201

    def test_update_article(self, auth_client, article: Article) -> None:
        """PATCH /api/articles/{id}/ updates and returns 200."""
        response = auth_client.patch(f"/api/articles/{article.pk}/", {"title": "Updated"})
        assert response.status_code == 200

    def test_delete_article(self, auth_client, article: Article) -> None:
        """DELETE /api/articles/{id}/ returns 204."""
        response = auth_client.delete(f"/api/articles/{article.pk}/")
        assert response.status_code == 204