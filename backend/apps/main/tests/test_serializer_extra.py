import pytest
from rest_framework.exceptions import ValidationError

from apps.main.serializers import ReactionSerializer, CommentCreateSerializer
from apps.main.tests.factories import ArticleFactory, CommentFactory, ReactionFactory
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_reaction_serializer_duplicate_detection():
    user = UserFactory()
    art = ArticleFactory()
    ReactionFactory(user=user, article=art)

    req = type("R", (), {"user": user})()
    ser = ReactionSerializer(data={"article": art.pk, "type": "like"}, context={"request": req})
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_comment_create_serializer_parent_mismatch():
    a1 = ArticleFactory()
    a2 = ArticleFactory()
    parent = CommentFactory(article=a1)
    req = type("R", (), {"user": UserFactory()})()
    ser = CommentCreateSerializer(data={"article": a2, "parent": parent.pk, "content": "x"}, context={"request": req})
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)
