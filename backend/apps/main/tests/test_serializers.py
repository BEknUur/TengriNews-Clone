import pytest
from types import SimpleNamespace

from rest_framework.exceptions import ValidationError

from apps.main.serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateUpdateSerializer,
    CommentCreateSerializer,
    ReactionSerializer,
    BookmarkSerializer,
)
from apps.main.tests.factories import (
    ArticleFactory,
    CommentFactory,
    ReactionFactory,
    TagFactory,
    BookmarkFactory,
)
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_article_list_get_author_none():
    art = ArticleFactory()
    # simulate missing author in-memory (don't modify DB constraints)
    art.author = None
    ser = ArticleListSerializer(art)
    assert ser.data["author"] is None


@pytest.mark.django_db
def test_article_detail_comments_and_reactions_count():
    art = ArticleFactory()
    # create comments and reactions
    CommentFactory(article=art)
    ReactionFactory(article=art)
    ReactionFactory(article=art)

    ser = ArticleDetailSerializer(art)
    assert isinstance(ser.data["comments"], list)
    assert ser.data["reactions_count"] == 2


@pytest.mark.django_db
def test_article_create_sets_author_and_tags():
    user = UserFactory()
    t1 = TagFactory()
    request = SimpleNamespace(user=user)
    data = {"title": "T", "slug": "s", "content": "c", "tags": [t1.pk], "is_published": False}
    ser = ArticleCreateUpdateSerializer(data=data, context={"request": request})
    assert ser.is_valid(), ser.errors
    art = ser.save()
    assert art.author_id == user.id
    assert list(art.tags.all())


@pytest.mark.django_db
def test_comment_create_parent_validation():
    a1 = ArticleFactory()
    a2 = ArticleFactory()
    parent = CommentFactory(article=a1)
    request = SimpleNamespace(user=UserFactory())
    data = {"article": a2, "parent": parent, "content": "hi"}
    ser = CommentCreateSerializer(data=data, context={"request": request})
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_reaction_serializer_requires_single_target_and_unique():
    user = UserFactory()
    art = ArticleFactory()
    # existing reaction
    ReactionFactory(user=user, article=art)

    # both targets set
    req = SimpleNamespace(user=user)
    ser = ReactionSerializer(data={"article": art.pk, "comment": 1, "type": "like"}, context={"request": req})
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)

    # duplicate reaction
    ser2 = ReactionSerializer(data={"article": art.pk, "type": "like"}, context={"request": req})
    with pytest.raises(ValidationError):
        ser2.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_bookmark_serializer_includes_article():
    b = BookmarkFactory()
    ser = BookmarkSerializer(b)
    assert "article" in ser.data and isinstance(ser.data["article"], dict)
