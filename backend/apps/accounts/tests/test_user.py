import pytest

from apps.accounts.models import CustomUser


@pytest.mark.django_db
class TestUserViewSet:
    def test_list_by_admin_returns_200(self, admin_client) -> None:
        response = admin_client.get("/api/accounts/users/")
        assert response.status_code == 200
        assert isinstance(response.data, list)

    def test_list_by_regular_user_returns_403(self, auth_client) -> None:
        response = auth_client.get("/api/accounts/users/")
        assert response.status_code == 403

    def test_retrieve_by_admin_returns_200(self, admin_client, user: CustomUser) -> None:
        response = admin_client.get(f"/api/accounts/users/{user.pk}/")
        assert response.status_code == 200
        assert response.data["id"] == user.pk

    def test_me_returns_200(self, auth_client, user: CustomUser) -> None:
        response = auth_client.get("/api/accounts/users/me/")
        assert response.status_code == 200
        assert response.data["email"] == user.email

    def test_partial_update_me_returns_200(self, auth_client) -> None:
        response = auth_client.patch(
            "/api/accounts/users/me/update/",
            {"first_name": "Updated"},
        )
        assert response.status_code == 200
        assert response.data["first_name"] == "Updated"
