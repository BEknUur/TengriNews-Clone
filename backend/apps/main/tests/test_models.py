import pytest
from django.core.exceptions import ValidationError
from apps.main.tests.factories import (
    ArticleFactory,
    CommentFactory,
    ReactionFactory,
    BookmarkFactory,
)


@pytest.mark.django_db
def test_article_factory_creates_article():
    art = ArticleFactory()
    assert art.pk is not None
    assert art.title
    assert art.is_published is True


@pytest.mark.django_db
def test_article_sets_published_at_on_publish():
    art = ArticleFactory(is_published=False, published_at=None)
    assert art.published_at is None
    art.is_published = True
    art.save()
    assert art.published_at is not None


@pytest.mark.django_db
def test_comment_clean_parent_must_same_article():
    a1 = ArticleFactory()
    a2 = ArticleFactory()
    parent = CommentFactory(article=a1)
    child = CommentFactory.build(article=a2, parent=parent)
    with pytest.raises(ValidationError):
        child.clean()


@pytest.mark.django_db
def test_reaction_clean_requires_exact_one_target():
    # both targets set -> invalid
    comment = CommentFactory()
    reaction_both = ReactionFactory.build(article=ArticleFactory(), comment=comment)
    with pytest.raises(ValidationError):
        reaction_both.clean()

    # neither target set -> invalid
    reaction_neither = ReactionFactory.build(article=None, comment=None)
    with pytest.raises(ValidationError):
        reaction_neither.clean()


@pytest.mark.django_db
def test_bookmark_str():
    b = BookmarkFactory()
    s = str(b)
    assert f"user={b.user_id}" in s and f"article={b.article_id}" in s