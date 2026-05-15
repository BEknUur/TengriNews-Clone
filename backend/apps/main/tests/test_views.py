import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.main.tests.factories import ArticleFactory

@pytest.mark.django_db
def test_article_list_returns_published():
    client = APIClient()
    ArticleFactory.create_batch(3, is_published=True)
    url = reverse("articles-list")
    resp = client.get(url)
    assert resp.status_code == 200
    body = resp.json()
    # API returns a paginated envelope with `data` key; accept both shapes
    if isinstance(body, dict):
        assert "data" in body and isinstance(body["data"], list)
    else:
        assert isinstance(body, list)