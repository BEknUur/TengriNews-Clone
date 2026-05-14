import pytest

from apps.main.models import Category


@pytest.mark.django_db
class TestCategoryViewSet:
    """Tests for CategoryViewSet endpoints."""



    def test_list_returns_200(self, api_client) -> None:
        """GET /api/categories/ returns 200 for unauthenticated user."""
        response = api_client.get("/api/categories/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_list_returns_data_key(self, api_client, category: Category) -> None:
        """Response body is a list (no pagination wrapper on categories)."""
        response = api_client.get("/api/categories/")
        assert response.status_code == 200
        assert isinstance(response.data, list), "Category list must be a plain list"


    def test_retrieve_returns_200(self, api_client, category: Category) -> None:
        """GET /api/categories/{id}/ returns 200."""
        response = api_client.get(f"/api/categories/{category.pk}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_retrieve_returns_correct_name(
        self, api_client, category: Category
    ) -> None:
        """Retrieve response contains correct category name."""
        response = api_client.get(f"/api/categories/{category.pk}/")
        assert (
            response.data["name"] == category.name
        ), f"Expected name={category.name}, got {response.data.get(chr(39)+'name'+chr(39))}"

    def test_retrieve_not_found_returns_404(self, api_client) -> None:
        """GET /api/categories/9999/ returns 404."""
        response = api_client.get("/api/categories/9999/")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


    def test_create_by_admin_returns_201(self, admin_client) -> None:
        """POST /api/categories/ by admin returns 201."""
        payload = {"name": "Sports", "slug": "sports"}
        response = admin_client.post("/api/categories/", payload)
        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {response.data}"

    def test_create_by_regular_user_returns_403(self, auth_client) -> None:
        """POST /api/categories/ by regular user returns 403."""
        payload = {"name": "Sports", "slug": "sports"}
        response = auth_client.post("/api/categories/", payload)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    def test_create_by_unauthenticated_returns_401(self, api_client) -> None:
        """POST /api/categories/ without token returns 401."""
        payload = {"name": "Sports", "slug": "sports"}
        response = api_client.post("/api/categories/", payload)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.parametrize(
        argnames=["name", "slug", "expected_status"],
        argvalues=[
<<<<<<< Updated upstream
            ("Tech", "tech", 400),  # duplicate — category fixture already has this
            ("Science", "science", 201),  # new — should succeed
        ],
=======
            ("Tech", "tech", 400),      
            ("Science", "science", 201),  
        ]
>>>>>>> Stashed changes
    )
    def test_create_parametrized(
        self,
        admin_client,
        category: Category,
        name: str,
        slug: str,
        expected_status: int,
    ) -> None:
        """Parametrized: create categories with different names/slugs."""
        response = admin_client.post("/api/categories/", {"name": name, "slug": slug})
        assert (
            response.status_code == expected_status
        ), f"name={name}: expected {expected_status}, got {response.status_code}: {response.data}"


    def test_partial_update_by_admin_returns_200(
        self, admin_client, category: Category
    ) -> None:
        """PATCH /api/categories/{id}/ by admin returns 200."""
        response = admin_client.patch(
            f"/api/categories/{category.pk}/", {"name": "Updated Tech"}
        )
        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.data}"
        assert response.data["name"] == "Updated Tech"

    def test_partial_update_not_found_returns_404(self, admin_client) -> None:
        """PATCH /api/categories/9999/ returns 404."""
        response = admin_client.patch("/api/categories/9999/", {"name": "X"})
        assert response.status_code == 404

    # --- Delete ---------------------------------------------------------------

    def test_delete_by_admin_returns_204(
        self, admin_client, category: Category
    ) -> None:
        """DELETE /api/categories/{id}/ by admin returns 204."""
        response = admin_client.delete(f"/api/categories/{category.pk}/")
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"

    def test_delete_not_found_returns_404(self, admin_client) -> None:
        """DELETE /api/categories/9999/ returns 404."""
        response = admin_client.delete("/api/categories/9999/")
        assert response.status_code == 404
