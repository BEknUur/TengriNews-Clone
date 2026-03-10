import pytest
from contextlib import nullcontext as does_not_raise
from typing import Any

from apps.accounts.models import CustomUser


@pytest.mark.django_db
class TestAuthViewSet:
    """Tests for AuthViewSet endpoints."""

    # ─── Register ────────────────────────────────────────────────────────────

    def test_register_returns_201(self, api_client) -> None:
        """POST /api/accounts/auth/register/ returns 201."""
        payload = {
            "email": "newuser@example.com",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post("/api/accounts/auth/register/", payload)
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.data}"
        )

    def test_register_duplicate_email_returns_400(self, api_client, user: CustomUser) -> None:
        """POST /api/accounts/auth/register/ with existing email returns 400."""
        payload = {
            "email": "testuser@example.com",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
            "first_name": "Dup",
            "last_name": "User",
        }
        response = api_client.post("/api/accounts/auth/register/", payload)
        assert response.status_code == 400, (
            f"Expected 400 for duplicate email, got {response.status_code}"
        )

    # ─── Login ────────────────────────────────────────────────────────────────

    def test_login_returns_200_with_tokens(self, api_client, user: CustomUser) -> None:
        """POST /api/accounts/auth/token/ returns 200 with access token."""
        payload = {"email": "testuser@example.com", "password": "testpass123"}
        response = api_client.post("/api/accounts/auth/token/", payload)
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.data}"
        )
        assert "access" in response.data, "Response must contain 'access' token"

    def test_login_wrong_password_returns_400(self, api_client, user: CustomUser) -> None:
        """POST /api/accounts/auth/token/ with wrong password returns 400."""
        payload = {"email": "testuser@example.com", "password": "wrongpass"}
        response = api_client.post("/api/accounts/auth/token/", payload)
        assert response.status_code == 400, (
            f"Expected 400 for wrong password, got {response.status_code}"
        )

    @pytest.mark.parametrize(
        argnames=["email", "password", "expected_status"],
        argvalues=[
            ("testuser@example.com", "testpass123", 200),
            ("testuser@example.com", "wrongpass", 400),
            ("notexist@example.com", "testpass123", 400),
        ]
    )
    def test_login_parametrized(
        self,
        api_client,
        user: CustomUser,
        email: str,
        password: str,
        expected_status: int,
    ) -> None:
        """Parametrized: test login with different credentials."""
        response = api_client.post(
            "/api/accounts/auth/token/",
            {"email": email, "password": password},
        )
        assert response.status_code == expected_status, (
            f"email={email}: expected {expected_status}, got {response.status_code}"
        )

    # ─── Token Refresh ────────────────────────────────────────────────────────

    def test_token_refresh_returns_200(self, api_client, user: CustomUser) -> None:
        """POST /api/accounts/auth/token/refresh/ returns 200 with new access."""
        login_response = api_client.post(
            "/api/accounts/auth/token/",
            {"email": "testuser@example.com", "password": "testpass123"},
        )
        refresh_token: str = login_response.data.get("refresh", "")
        assert refresh_token, "Login must return a 'refresh' token"

        response = api_client.post(
            "/api/accounts/auth/token/refresh/",
            {"refresh": refresh_token},
        )
        assert response.status_code == 200, (
            f"Expected 200 on refresh, got {response.status_code}: {response.data}"
        )
        assert "access" in response.data, "Refresh response must contain 'access' token"
