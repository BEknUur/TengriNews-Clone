# Python modules
from typing import Any

# Third-party modules
import pytest

# Project modules
from apps.main.models import Tag


@pytest.mark.django_db
class TestTagViewSet:
    """Tests for TagViewSet endpoints."""

    def test_list_returns_200(self, api_client: Any) -> None:
        """GET /api/tags/ returns 200 for unauthenticated user."""
        response = api_client.get("/api/tags/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_list_returns_list(self, api_client: Any, tag: Tag) -> None:
        """Response body is a plain list."""
        response = api_client.get("/api/tags/")
        assert isinstance(response.data, list), "Tag list must be a plain list"

    def test_retrieve_returns_200(self, api_client: Any, tag: Tag) -> None:
        """GET /api/tags/{id}/ returns 200."""
        response = api_client.get(f"/api/tags/{tag.pk}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_retrieve_correct_name(self, api_client: Any, tag: Tag) -> None:
        """Retrieve returns correct tag name."""
        response = api_client.get(f"/api/tags/{tag.pk}/")
        assert (
            response.data["name"] == tag.name
        ), f"Expected name={tag.name}, got {response.data.get('name')}"

    def test_retrieve_not_found_returns_404(self, api_client: Any) -> None:
        """GET /api/tags/9999/ returns 404."""
        response = api_client.get("/api/tags/9999/")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_create_by_admin_returns_201(self, admin_client: Any) -> None:
        """POST /api/tags/ by admin returns 201."""
        payload = {"name": "Python", "slug": "python"}
        response = admin_client.post("/api/tags/", payload)
        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {response.data}"

    def test_create_by_regular_user_returns_403(self, auth_client: Any) -> None:
        """POST /api/tags/ by regular user returns 403."""
        response = auth_client.post("/api/tags/", {"name": "Python", "slug": "python"})
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    def test_create_unauthenticated_returns_401(self, api_client: Any) -> None:
        """POST /api/tags/ without token returns 401."""
        response = api_client.post("/api/tags/", {"name": "Python", "slug": "python"})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.parametrize(
        argnames=["name", "slug", "expected_status"],
        argvalues=[
            ("Django", "django", 400),  # duplicate - tag fixture already exists
            ("FastAPI", "fastapi", 201),  # new - should succeed
        ],
    )
    def test_create_parametrized(
        self,
        admin_client: Any,
        tag: Tag,
        name: str,
        slug: str,
        expected_status: int,
    ) -> None:
        """Parametrized: create tags with different names/slugs."""
        response = admin_client.post("/api/tags/", {"name": name, "slug": slug})
        assert (
            response.status_code == expected_status
        ), f"name={name}: expected {expected_status}, got {response.status_code}: {response.data}"

    def test_partial_update_by_admin_returns_200(self, admin_client: Any, tag: Tag) -> None:
        """PATCH /api/tags/{id}/ by admin returns 200."""
        response = admin_client.patch(
            f"/api/tags/{tag.pk}/", {"name": "Updated Django"}
        )
        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.data}"
        assert response.data["name"] == "Updated Django"

    def test_partial_update_not_found_returns_404(self, admin_client: Any) -> None:
        """PATCH /api/tags/9999/ returns 404."""
        response = admin_client.patch("/api/tags/9999/", {"name": "X"})
        assert response.status_code == 404

    def test_delete_by_admin_returns_204(self, admin_client: Any, tag: Tag) -> None:
        """DELETE /api/tags/{id}/ by admin returns 204."""
        response = admin_client.delete(f"/api/tags/{tag.pk}/")
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"

    def test_delete_not_found_returns_404(self, admin_client: Any) -> None:
        """DELETE /api/tags/9999/ returns 404."""
        response = admin_client.delete("/api/tags/9999/")
        assert response.status_code == 404
