import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient
from django.core.cache import caches

from apps.main.models import Article
from apps.main.utils.cache import make_article_detail_key


@pytest.mark.django_db
@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        "article_cache": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    }
)
def test_article_detail_cache_set_and_hit():
    User = get_user_model()
    user = User.objects.create_user(
        email="u1@example.com", first_name="U1", last_name="One", password="pass"
    )
    article = Article.objects.create(
        title="Hello",
        slug="hello",
        content="world",
        author=user,
    )

    client = APIClient()

    url = f"/api/articles/{article.pk}/"
    # first request primes cache
    resp1 = client.get(url)
    assert resp1.status_code == 200

    cache = caches["article_cache"]
    key = make_article_detail_key(article.pk)
    assert cache.get(key) is not None

    # second request should still succeed and return same data
    resp2 = client.get(url)
    assert resp2.status_code == 200
    assert resp2.data == resp1.data


@pytest.mark.django_db
@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        "article_cache": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    }
)
def test_cache_invalidation_on_update_and_delete():
    User = get_user_model()
    user = User.objects.create_user(
        email="u2@example.com", first_name="U2", last_name="Two", password="pass"
    )
    article = Article.objects.create(
        title="Before",
        slug="before",
        content="text",
        author=user,
    )

    client = APIClient()
    url = f"/api/articles/{article.pk}/"

    # prime cache
    resp = client.get(url)
    assert resp.status_code == 200
    cache = caches["article_cache"]
    key = make_article_detail_key(article.pk)
    assert cache.get(key) is not None

    # update article -> signal should invalidate cache
    article.title = "After"
    article.save()
    assert cache.get(key) is None

    # prime again and then delete
    client.get(url)
    assert cache.get(key) is not None
    article.delete()
    assert cache.get(key) is None
