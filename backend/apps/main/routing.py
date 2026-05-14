# Django modules
from django.urls import path

# Project modules
from apps.main.consumers import NewsConsumer

websocket_urlpatterns = [
    path("ws/news/", NewsConsumer.as_asgi()),
]
