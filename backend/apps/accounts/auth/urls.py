# Third-party modules
from rest_framework.routers import DefaultRouter

# Django modules
from django.urls import path, include

# Project modules
from apps.accounts.auth.views import AuthViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")

urlpatterns = [
    path("", include(router.urls)),
]
