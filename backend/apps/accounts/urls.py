# Django modules
from django.urls import include, path

# Third-party modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.accounts.views.auth import AuthViewSet
from apps.accounts.views.user import UserViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
