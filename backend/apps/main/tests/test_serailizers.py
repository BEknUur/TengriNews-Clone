# Python modules
from typing import Any

# Django modules
from django.test import RequestFactory

# Third-party modules
import pytest

# Project modules
from apps.main.serializers import (
    ArticleCreateUpdateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    CategorySerializer,
    TagSerializer,
)


@pytest.mark.django_db
def test_category_serializer_fields(category: Any) -> None:
    """Test `test_category_serializer_fields`."""
    data = CategorySerializer(category).data

    assert data["id"] == category.id
    assert data["name"] == category.name
    assert data["slug"] == category.slug
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.django_db
def test_tag_serializer_fields(tag: Any) -> None:
    """Test `test_tag_serializer_fields`."""
    data = TagSerializer(tag).data

    assert data["id"] == tag.id
    assert data["name"] == tag.name
    assert data["slug"] == tag.slug
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.django_db
def test_article_list_serializer_returns_nested_category_and_tags(article: Any, tag: Any) -> None:
    """Test `test_article_list_serializer_returns_nested_category_and_tags`."""
    article.tags.add(tag)

    data = ArticleListSerializer(article).data

    assert data["category"]["id"] == article.category_id
    assert data["category"]["name"] == article.category.name
    assert data["tags"][0]["id"] == tag.id
    assert data["author"]["id"] == article.author_id


@pytest.mark.django_db
def test_article_detail_serializer_contains_content_comments_and_reactions(article: Any) -> None:
    """Test `test_article_detail_serializer_contains_content_comments_and_reactions`."""
    data = ArticleDetailSerializer(article).data

    assert data["content"] == article.content
    assert "comments" in data
    assert "reactions_count" in data


@pytest.mark.django_db
def test_article_create_update_serializer_accepts_category_and_tag_ids(
    rf: Any,
    user: Any,
    category: Any,
    tag: Any,
) -> None:
    """Test `test_article_create_update_serializer_accepts_category_and_tag_ids`."""
    request = rf.post("/api/articles/")
    request.user = user

    serializer = ArticleCreateUpdateSerializer(
        data={
            "title": "Serializer Article",
            "slug": "serializer-article",
            "excerpt": "Short text",
            "content": "Full content",
            "category": category.id,
            "tags": [tag.id],
            "is_published": True,
        },
        context={"request": request},
    )

    assert serializer.is_valid(), serializer.errors
    article = serializer.save()
    assert article.category_id == category.id
    assert list(article.tags.values_list("id", flat=True)) == [tag.id]


@pytest.fixture
def rf() -> RequestFactory:
    """Fixture `rf`."""
    return RequestFactory()
