# Python modules
from typing import Any

# Django modules
from django.db import connection
from django.test.utils import CaptureQueriesContext

# Third-party modules
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Project modules
from apps.accounts.models import CustomUser
from apps.main.models import Article, Category, Comment, Reaction, Tag


@pytest.fixture
def user(db: Any) -> CustomUser:
    return CustomUser.objects.create_user(
        email="perf@example.com",
        password="pass123",
        first_name="Perf",
        last_name="User",
    )


@pytest.fixture
def auth_client(user: CustomUser) -> APIClient:
    client = APIClient()
    token = str(RefreshToken.for_user(user).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def category(db: Any) -> Category:
    return Category.objects.create(name="PerfCat", slug="perf-cat")


def make_article(
    user: CustomUser,
    category: Category,
    slug: str,
    num_comments: int = 0,
    replies_per_comment: int = 0,
) -> Article:
    tag = Tag.objects.get_or_create(name="PerfTag", slug="perf-tag")[0]
    article = Article.objects.create(
        title=f"Perf {slug}",
        slug=slug,
        content="x",
        author=user,
        category=category,
        is_published=True,
    )
    article.tags.set([tag])
    for i in range(num_comments):
        comment = Comment.objects.create(article=article, user=user, content=f"C{i}")
        for j in range(replies_per_comment):
            Comment.objects.create(article=article, user=user, parent=comment, content=f"R{j}")
    Reaction.objects.create(article=article, user=user, type="like")
    return article


def count_queries(client: APIClient, url: str) -> int:
    with CaptureQueriesContext(connection) as ctx:
        client.get(url)
    return len(ctx.captured_queries)


@pytest.mark.django_db
class TestNoN1OnArticleDetail:
    def test_query_count_fixed_regardless_of_comment_count(
        self,
        auth_client: APIClient,
        user: CustomUser,
        category: Category,
    ) -> None:
        small = make_article(user, category, "small-perf", num_comments=2, replies_per_comment=2)
        large = make_article(user, category, "large-perf", num_comments=10, replies_per_comment=3)

        q_small = count_queries(auth_client, f"/api/articles/{small.pk}/")
        q_large = count_queries(auth_client, f"/api/articles/{large.pk}/")

        assert q_small == q_large, (
            f"N+1 detected on detail: {q_small} queries for 2 comments, "
            f"{q_large} queries for 10 comments"
        )

    def test_reactions_count_correct_without_extra_query(
        self, auth_client: APIClient, user: CustomUser, category: Category
    ) -> None:
        article = make_article(user, category, "react-perf", num_comments=1)
        u2 = CustomUser.objects.create_user(
            email="reactor@example.com", password="x", first_name="R", last_name="X"
        )
        Reaction.objects.create(article=article, user=u2, type="love")

        response = auth_client.get(f"/api/articles/{article.pk}/")
        assert response.status_code == 200
        assert response.data["reactions_count"] == 2

    def test_replies_included_in_response(
        self, auth_client: APIClient, user: CustomUser, category: Category
    ) -> None:
        article = make_article(user, category, "reply-perf", num_comments=2, replies_per_comment=3)
        response = auth_client.get(f"/api/articles/{article.pk}/")

        assert response.status_code == 200
        comments = response.data["comments"]
        assert len(comments) == 2
        assert all(len(c["replies"]) == 3 for c in comments)

    def test_replies_capped_at_one_level(
        self, auth_client: APIClient, user: CustomUser, category: Category
    ) -> None:
        article = make_article(user, category, "depth-perf", num_comments=2, replies_per_comment=2)
        response = auth_client.get(f"/api/articles/{article.pk}/")

        for comment in response.data["comments"]:
            for reply in comment["replies"]:
                assert reply["replies"] == []


@pytest.mark.django_db
class TestNoN1OnArticleList:
    def test_query_count_fixed_regardless_of_article_count(
        self,
        auth_client: APIClient,
        user: CustomUser,
        category: Category,
    ) -> None:
        for i in range(3):
            make_article(user, category, f"list-s{i}")

        q_small = count_queries(auth_client, "/api/articles/")

        for i in range(7):
            make_article(user, category, f"list-l{i}")

        q_large = count_queries(auth_client, "/api/articles/")

        assert q_small == q_large, (
            f"N+1 detected on list: {q_small} queries for 3 articles, "
            f"{q_large} queries for 10 articles"
        )
