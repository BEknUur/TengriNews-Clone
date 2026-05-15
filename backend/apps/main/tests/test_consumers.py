import json
import pytest

from apps.main.consumers import NewsConsumer
from apps.main.realtime import NEWS_GROUP_NAME


class DummyChannelLayer:
    def __init__(self):
        self.added = []
        self.discarded = []
        self.messages = []

    async def group_add(self, group, channel):
        self.added.append((group, channel))

    async def group_discard(self, group, channel):
        self.discarded.append((group, channel))

    async def group_send(self, group, message):
        self.messages.append((group, message))


@pytest.mark.asyncio
async def test_news_consumer_connect_receive_and_broadcast():
    consumer = NewsConsumer()
    consumer.channel_layer = DummyChannelLayer()
    consumer.channel_name = "test-channel"

    sent = []

    async def fake_send(text_data=None, bytes_data=None):
        sent.append(text_data)

    consumer.send = fake_send
    async def fake_accept():
        return None
    consumer.accept = fake_accept

    # connect should add to group and send welcome
    await consumer.connect()
    assert consumer.channel_layer.added == [(NEWS_GROUP_NAME, "test-channel")]
    assert sent, "welcome message was not sent"
    data = json.loads(sent[-1])
    assert data["type"] == "welcome"

    # receive should echo
    sent.clear()
    await consumer.receive(text_data="hello world")
    assert sent, "echo message was not sent"
    data = json.loads(sent[-1])
    assert data["type"] == "echo"
    assert data["message"] == "hello world"

    # article_created should forward payload
    sent.clear()
    await consumer.article_created({"payload": {"title": "New"}})
    data = json.loads(sent[-1])
    assert data["type"] == "article_created"
    assert data["title"] == "New"

    # comment_created should forward payload
    sent.clear()
    await consumer.comment_created({"payload": {"content": "Nice"}})
    data = json.loads(sent[-1])
    assert data["type"] == "comment_created"
    assert data["content"] == "Nice"

    # disconnect should remove from group
    await consumer.disconnect(code=1000)
    assert consumer.channel_layer.discarded == [(NEWS_GROUP_NAME, "test-channel")]
