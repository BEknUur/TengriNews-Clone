# Python modules
from typing import Any

# Third-party modules
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import AsyncClient

try:
    import fakeredis
except Exception:
    fakeredis = None

# Project modules
from apps.accounts.models import CustomUser
from apps.main.models import Article, Category, Tag


@pytest.fixture
def api_client() -> APIClient:
    """Returns a DRF APIClient instance."""
    return APIClient()


@pytest.fixture
def async_client() -> AsyncClient:
    """Returns an AsyncClient for async view tests."""
    return AsyncClient()


@pytest.fixture
def user(db: Any) -> CustomUser:
    """Creates and returns a regular user."""
    return CustomUser.objects.create_user(
        email="testuser@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user(db: Any) -> CustomUser:
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


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear Django caches before/after each test to avoid leakage."""
    from django.core.cache import caches
    from django.conf import settings
    for name in list(caches):
        try:
            caches[name].clear()
        except Exception:
            pass
    # Disable rate limiting during tests to avoid 429 flakiness
    try:
        settings.DISABLE_RATE_LIMIT = True
    except Exception:
        pass
    yield
    for name in list(caches):
        try:
            caches[name].clear()
        except Exception:
            pass


@pytest.fixture
def fake_redis(monkeypatch):
    """Provide a fakeredis instance and patch redis client usage if available."""
    if not fakeredis:
        pytest.skip("fakeredis is not installed")
    client = fakeredis.FakeServer()
    # if project uses redis.StrictRedis or a redis client wrapper, tests can
    # monkeypatch it to use fakeredis.FakeStrictRedis(server=client)
    return client


@pytest.fixture
def admin_client(api_client: APIClient, admin_user: CustomUser) -> APIClient:
    """Returns an APIClient authenticated as an admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client


@pytest.fixture
def category(db: Any) -> Category:
    """Creates and returns a test Category."""
    return Category.objects.create(name="Tech", slug="tech")


@pytest.fixture
def tag(db: Any) -> Tag:
    """Creates and returns a test Tag."""
    return Tag.objects.create(name="Django", slug="django")


@pytest.fixture
def article(db: Any, user: CustomUser, category: Category) -> Article:
    """Creates and returns a published test Article."""
    return Article.objects.create(
        title="Test Article",
        slug="test-article",
        content="Some content",
        author=user,
        category=category,
        is_published=True,
    )
