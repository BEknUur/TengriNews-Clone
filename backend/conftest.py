import pytest
from dataclasses import dataclass
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import CustomUser
from apps.main.models import Category, Tag, Article



@dataclass
class AuthData:
    """Holds authenticated user and its token."""
    user: CustomUser
    token: str



@pytest.fixture
def api_client() -> APIClient:
    """Returns a DRF APIClient instance."""
    return APIClient()


@pytest.fixture
def user(db) -> CustomUser:
    """Creates and returns a regular user."""
    return CustomUser.objects.create_user(
        email="testuser@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user(db) -> CustomUser:
    """Creates and returns a superuser (passes IsAdminOnly permission)."""
    return CustomUser.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def auth_client(api_client: APIClient, user: CustomUser) -> APIClient:
    """Returns an APIClient authenticated as a regular user."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client


@pytest.fixture
def admin_client(api_client: APIClient, admin_user: CustomUser) -> APIClient:
    """Returns an APIClient authenticated as an admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client



@pytest.fixture
def category(db) -> Category:
    """Creates and returns a test Category."""
    return Category.objects.create(name="Tech", slug="tech")


@pytest.fixture
def tag(db) -> Tag:
    """Creates and returns a test Tag."""
    return Tag.objects.create(name="Django", slug="django")


@pytest.fixture
def article(db, user: CustomUser, category: Category) -> Article:
    """Creates and returns a published test Article."""
    return Article.objects.create(
        title="Test Article",
        slug="test-article",
        content="Some content",
        author=user,
        category=category,
        is_published=True,
    )