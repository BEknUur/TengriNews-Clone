import pytest

from apps.main.models import Comment, Article
from apps.accounts.models import CustomUser


@pytest.fixture
def comment(db, user: CustomUser, article: Article) -> Comment:
    """Creates and returns a test Comment."""
    return Comment.objects.create(
        article=article,
        user=user,
        content="Test comment content",
    )


@pytest.mark.django_db
class TestCommentViewSet:
    """Tests for CommentViewSet endpoints."""

    def test_list_returns_200(self, api_client) -> None:
        """GET /api/comments/ returns 200."""
        response = api_client.get("/api/comments/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_list_returns_list(self, api_client, comment: Comment) -> None:
        """Response body is a plain list."""
        response = api_client.get("/api/comments/")
        assert isinstance(response.data, list), "Comment list must be a plain list"

    def test_retrieve_returns_200(self, api_client, comment: Comment) -> None:
        """GET /api/comments/{id}/ returns 200."""
        response = api_client.get(f"/api/comments/{comment.pk}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_retrieve_not_found_returns_404(self, api_client) -> None:
        """GET /api/comments/9999/ returns 404."""
        response = api_client.get("/api/comments/9999/")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_create_authenticated_returns_201(
        self, auth_client, article: Article
    ) -> None:
        """POST /api/comments/ by authenticated user returns 201."""
        payload = {"article": article.pk, "content": "This is a great read!"}
        response = auth_client.post("/api/comments/", payload)
        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {response.data}"

    def test_create_unauthenticated_returns_401(
        self, api_client, article: Article
    ) -> None:
        """POST /api/comments/ without token returns 401."""
        response = api_client.post(
            "/api/comments/", {"article": article.pk, "content": "Test"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_partial_update_by_author_returns_200(
        self, auth_client, comment: Comment
    ) -> None:
        """PATCH /api/comments/{id}/ by comment author returns 200."""
        response = auth_client.patch(
            f"/api/comments/{comment.pk}/", {"content": "Updated content"}
        )
        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.data}"

    def test_partial_update_not_found_returns_404(self, auth_client) -> None:
        """PATCH /api/comments/9999/ returns 404."""
        response = auth_client.patch("/api/comments/9999/", {"content": "X"})
        assert response.status_code == 404

    def test_delete_by_author_returns_204(self, auth_client, comment: Comment) -> None:
        """DELETE /api/comments/{id}/ by comment author returns 204."""
        response = auth_client.delete(f"/api/comments/{comment.pk}/")
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"

    def test_delete_not_found_returns_404(self, auth_client) -> None:
        """DELETE /api/comments/9999/ returns 404."""
        response = auth_client.delete("/api/comments/9999/")
        assert response.status_code == 404

    @pytest.mark.parametrize(
        argnames=["content", "expected_status"],
        argvalues=[
            ("Valid comment content", 201),
            ("", 400),
        ],
    )
    def test_create_content_validation_parametrized(
        self,
        auth_client,
        article: Article,
        content: str,
        expected_status: int,
    ) -> None:
        """Parametrized: comment creation with valid and invalid content."""
        response = auth_client.post(
            "/api/comments/", {"article": article.pk, "content": content}
        )
        assert (
            response.status_code == expected_status
        ), f"content='{content}': expected {expected_status}, got {response.status_code}: {response.data}"
