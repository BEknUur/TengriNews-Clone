"""WebSocket routes for the main app."""

from django.urls import path

from apps.main.consumers import NewsConsumer

websocket_urlpatterns = [
    path("ws/news/", NewsConsumer.as_asgi()),
]