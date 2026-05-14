"""WebSocket consumer for realtime news notifications."""

from __future__ import annotations

import json

from channels.generic.websocket import AsyncWebsocketConsumer

from apps.main.realtime import NEWS_GROUP_NAME


class NewsConsumer(AsyncWebsocketConsumer):
    """Send a welcome message, echo messages, and receive broadcast events."""

    async def connect(self) -> None:
        await self.channel_layer.group_add(NEWS_GROUP_NAME, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"type": "welcome", "message": "connected"}))

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(NEWS_GROUP_NAME, self.channel_name)

    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        message = text_data or (bytes_data.decode("utf-8") if bytes_data else "")
        await self.send(text_data=json.dumps({"type": "echo", "message": message}))

    async def article_created(self, event: dict) -> None:
        await self.send(text_data=json.dumps({"type": "article_created", **event["payload"]}))

    async def comment_created(self, event: dict) -> None:
        await self.send(text_data=json.dumps({"type": "comment_created", **event["payload"]}))