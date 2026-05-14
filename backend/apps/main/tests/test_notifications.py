import pytest

from apps.accounts.models import CustomUser
from apps.main.models import Article, Category, Comment


class DummyChannelLayer:
    def __init__(self) -> None:
        self.messages: list[tuple[str, dict]] = []

    async def group_send(self, group: str, message: dict) -> None:
        self.messages.append((group, message))


@pytest.mark.django_db
class TestRealtimeNotifications:
    def test_article_create_broadcasts_event(self, monkeypatch, user: CustomUser) -> None:
        from apps.main import realtime

        channel_layer = DummyChannelLayer()
        monkeypatch.setattr(realtime, "get_channel_layer", lambda: channel_layer)

        category = Category.objects.create(name="Tech", slug="tech")
        Article.objects.create(
            title="New article",
            slug="new-article",
            content="Body",
            author=user,
            category=category,
            is_published=True,
        )

        assert len(channel_layer.messages) == 1
        group, message = channel_layer.messages[0]
        assert group == realtime.NEWS_GROUP_NAME
        assert message["type"] == "article_created"
        assert message["payload"]["title"] == "New article"
        assert message["payload"]["author"]["id"] == user.id

    def test_comment_create_broadcasts_event(
        self,
        monkeypatch,
        user: CustomUser,
        article: Article,
    ) -> None:
        from apps.main import realtime

        channel_layer = DummyChannelLayer()
        monkeypatch.setattr(realtime, "get_channel_layer", lambda: channel_layer)

        Comment.objects.create(article=article, user=user, content="Nice read")

        assert len(channel_layer.messages) == 1
        group, message = channel_layer.messages[0]
        assert group == realtime.NEWS_GROUP_NAME
        assert message["type"] == "comment_created"
        assert message["payload"]["content"] == "Nice read"
        assert message["payload"]["article"] == article.id