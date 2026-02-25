# Third-party modules
from rest_framework.routers import DefaultRouter

# Django modules
from django.urls import path, include

# Project modules
from apps.accounts.auth.views import AuthViewSet
from apps.accounts.views import UserViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
