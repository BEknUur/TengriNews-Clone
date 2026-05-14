# Python modules
from typing import Any

# Third-party modules
import pytest

# Project modules
from apps.main.models import Bookmark


@pytest.mark.django_db
class TestBookmarkAPI:
    """TestBookmarkAPI class."""
    def test_add_bookmark(self, auth_client: Any, article: Any) -> None:
        """Test `test_add_bookmark`."""
        response = auth_client.post(f"/api/articles/{article.pk}/bookmark/")

        assert response.status_code == 201
        assert Bookmark.objects.filter(
            article=article,
            deleted_at__isnull=True,
        ).exists()

    def test_duplicate_bookmark_does_not_create_second_active_bookmark(
        self,
        auth_client: Any,
        article: Any,
    ) -> None:
        """Test `test_duplicate_bookmark_does_not_create_second_active_bookmark`."""
        auth_client.post(f"/api/articles/{article.pk}/bookmark/")
        response = auth_client.post(f"/api/articles/{article.pk}/bookmark/")

        assert response.status_code == 200
        assert Bookmark.objects.filter(
            article=article,
            deleted_at__isnull=True,
        ).count() == 1

    def test_list_bookmarks(self, auth_client: Any, article: Any) -> None:
        """Test `test_list_bookmarks`."""
        auth_client.post(f"/api/articles/{article.pk}/bookmark/")
        response = auth_client.get("/api/bookmarks/")

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["article"]["id"] == article.pk

    def test_delete_bookmark(self, auth_client: Any, article: Any) -> None:
        """Test `test_delete_bookmark`."""
        auth_client.post(f"/api/articles/{article.pk}/bookmark/")
        response = auth_client.delete(f"/api/articles/{article.pk}/bookmark/")

        assert response.status_code == 200
        assert not Bookmark.objects.filter(
            article=article,
            deleted_at__isnull=True,
        ).exists()

    def test_anonymous_user_cannot_bookmark(self, api_client: Any, article: Any) -> None:
        """Test `test_anonymous_user_cannot_bookmark`."""
        response = api_client.post(f"/api/articles/{article.pk}/bookmark/")

        assert response.status_code == 401
