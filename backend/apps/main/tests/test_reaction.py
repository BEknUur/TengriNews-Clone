# Python modules
from typing import Any
import json

# Third-party modules
import pytest

# Project modules
from apps.accounts.models import CustomUser
from apps.main.models import Article, Comment, Reaction


def _resp_data(response):
    """Return parsed response body similar to DRF `response.data`.

    Handles DRF Response objects and Django JsonResponse/HttpResponse.
    """
    if hasattr(response, "data"):
        return response.data
    try:
        return json.loads(response.content.decode())
    except Exception:
        return None


@pytest.fixture
def comment(db: Any, user: CustomUser, article: Article) -> Comment:
    """Creates and returns a test Comment."""
    return Comment.objects.create(
        article=article,
        user=user,
        content="Test comment content",
    )


@pytest.fixture
def reaction_on_article(db: Any, user: CustomUser, article: Article) -> Reaction:
    """Creates and returns a Reaction on an article."""
    return Reaction.objects.create(
        user=user,
        article=article,
        type=Reaction.ReactionType.LIKE,
    )


@pytest.fixture
def reaction_on_comment(db: Any, user: CustomUser, comment: Comment) -> Reaction:
    """Creates and returns a Reaction on a comment."""
    return Reaction.objects.create(
        user=user,
        comment=comment,
        type=Reaction.ReactionType.LOVE,
    )


@pytest.mark.django_db
class TestReactionViewSet:
    """Tests for ReactionViewSet endpoints."""

    # --- List -----------------------------------------------------------------

    def test_list_returns_200(self, api_client: Any) -> None:
        """GET /api/reactions/ returns 200 for unauthenticated user."""
        response = api_client.get("/api/reactions/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_list_returns_list(self, api_client: Any, reaction_on_article: Reaction) -> None:
        """Response body is a plain list."""
        response = api_client.get("/api/reactions/")
        body = _resp_data(response)
        assert isinstance(body, list), "Reaction list must be a plain list"

    # --- Retrieve -------------------------------------------------------------

    def test_retrieve_returns_200(self, api_client: Any, reaction_on_article: Reaction) -> None:
        """GET /api/reactions/{id}/ returns 200."""
        response = api_client.get(f"/api/reactions/{reaction_on_article.pk}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_retrieve_returns_correct_type(self, api_client: Any, reaction_on_article: Reaction) -> None:
        """Retrieve response contains correct reaction type."""
        response = api_client.get(f"/api/reactions/{reaction_on_article.pk}/")
        body = _resp_data(response)
        assert (
            body["type"] == Reaction.ReactionType.LIKE
        ), f"Expected type={Reaction.ReactionType.LIKE}, got {body.get('type')}"

    def test_retrieve_not_found_returns_404(self, api_client: Any) -> None:
        """GET /api/reactions/9999/ returns 404."""
        response = api_client.get("/api/reactions/9999/")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # --- Create ---------------------------------------------------------------

    def test_create_reaction_on_article_returns_201(self, auth_client: Any, article: Article) -> None:
        """POST /api/reactions/ with article target returns 201."""
        payload = {"article": article.pk, "type": Reaction.ReactionType.LIKE}
        response = auth_client.post("/api/reactions/", payload)
        body = _resp_data(response)
        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {body}"

    def test_create_reaction_on_comment_returns_201(self, auth_client: Any, comment: Comment) -> None:
        """POST /api/reactions/ with comment target returns 201."""
        payload = {"comment": comment.pk, "type": Reaction.ReactionType.LOVE}
        response = auth_client.post("/api/reactions/", payload)
        body = _resp_data(response)
        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {body}"

    def test_create_unauthenticated_returns_401(self, api_client: Any, article: Article) -> None:
        """POST /api/reactions/ without token returns 401."""
        response = api_client.post(
            "/api/reactions/", {"article": article.pk, "type": Reaction.ReactionType.LIKE}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_create_duplicate_reaction_returns_400(self, auth_client: Any, reaction_on_article: Reaction, article: Article) -> None:
        """POST /api/reactions/ duplicate reaction on same article returns 400."""
        payload = {"article": article.pk, "type": Reaction.ReactionType.DISLIKE}
        response = auth_client.post("/api/reactions/", payload)
        body = _resp_data(response)
        assert (
            response.status_code == 400
        ), f"Expected 400 for duplicate reaction, got {response.status_code}: {body}"

    def test_create_both_targets_returns_400(self, auth_client: Any, article: Article, comment: Comment) -> None:
        """POST /api/reactions/ with both article and comment returns 400."""
        payload = {"article": article.pk, "comment": comment.pk, "type": Reaction.ReactionType.LIKE}
        response = auth_client.post("/api/reactions/", payload)
        body = _resp_data(response)
        assert (
            response.status_code == 400
        ), f"Expected 400 when both targets provided, got {response.status_code}: {body}"

    def test_create_no_target_returns_400(self, auth_client: Any) -> None:
        """POST /api/reactions/ with no target returns 400."""
        payload = {"type": Reaction.ReactionType.LIKE}
        response = auth_client.post("/api/reactions/", payload)
        body = _resp_data(response)
        assert (
            response.status_code == 400
        ), f"Expected 400 when no target provided, got {response.status_code}: {body}"

    @pytest.mark.parametrize(
        argnames=["reaction_type", "expected_status"],
        argvalues=[
            (Reaction.ReactionType.LIKE, 201),
            (Reaction.ReactionType.DISLIKE, 201),
            (Reaction.ReactionType.LOVE, 201),
            (Reaction.ReactionType.LAUGH, 201),
            ("invalid_type", 400),
        ],
    )
    def test_create_reaction_types_parametrized(
        self,
        auth_client: Any,
        article: Article,
        reaction_type: str,
        expected_status: int,
    ) -> None:
        """Parametrized: create reactions with different types."""
        response = auth_client.post(
            "/api/reactions/", {"article": article.pk, "type": reaction_type}
        )
        body = _resp_data(response)
        assert (
            response.status_code == expected_status
        ), f"type={reaction_type}: expected {expected_status}, got {response.status_code}: {body}"

    # --- Delete ---------------------------------------------------------------

    def test_delete_by_authenticated_returns_204(self, auth_client: Any, reaction_on_article: Reaction) -> None:
        """DELETE /api/reactions/{id}/ by authenticated user returns 204."""
        response = auth_client.delete(f"/api/reactions/{reaction_on_article.pk}/")
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"

    def test_delete_not_found_returns_404(self, auth_client: Any) -> None:
        """DELETE /api/reactions/9999/ returns 404."""
        response = auth_client.delete("/api/reactions/9999/")
        assert response.status_code == 404

    def test_delete_unauthenticated_returns_401(
        self, api_client: Any, reaction_on_article: Reaction
    ) -> None:
        """DELETE /api/reactions/{id}/ without token returns 401."""
        response = api_client.delete(f"/api/reactions/{reaction_on_article.pk}/")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
