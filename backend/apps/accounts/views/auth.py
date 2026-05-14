from __future__ import annotations

# Python modules
import logging
from typing import Any

# Django modules
from django.conf import settings
from django.db import transaction

# Third-party modules
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.throttling import BaseThrottle, ScopedRateThrottle
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

# Project modules
from apps.core.decorators import validate_serializer_data
from apps.core.mixins import DRFResponseMixin
from apps.core.throttling import CustomAnonRateThrottle, CustomUserRateThrottle
from apps.accounts.schema_serializers import (
    AccessTokenResponseSerializer,
    LoginRequestSerializer,
    RefreshTokenRequestSerializer,
    RegisterRequestSerializer,
    RegisterResponseSerializer,
    TokenPairResponseSerializer,
)
from apps.accounts.serializers import LoginSerializer, RegistrationSerializer
from apps.accounts.tasks import send_welcome_email_task

logger = logging.getLogger(__name__)


class AuthViewSet(DRFResponseMixin, ViewSet):
    """Handles registration, login, and token refresh."""

    permission_classes = [AllowAny]
    throttle_classes = [
        CustomAnonRateThrottle,
        CustomUserRateThrottle,
        ScopedRateThrottle,
    ]

    def get_throttles(self) -> list[BaseThrottle]:
        """Assign scoped throttle rates for login/register actions."""
        if getattr(settings, "DISABLE_AUTH_THROTTLING", False):
            return []

        if self.action == "login":
            self.throttle_scope = "auth_login"
        elif self.action == "register":
            self.throttle_scope = "auth_register"
        return super().get_throttles()

    @extend_schema(
        summary="Obtain JWT tokens",
        request=LoginRequestSerializer,
        responses={
            HTTP_200_OK: TokenPairResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid credentials"),
            HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(description="Rate limit exceeded"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(methods=["post"], detail=False, url_path="token", url_name="token")
    @validate_serializer_data(serializer_class=LoginSerializer)
    def login(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Authenticate a user and return access + refresh tokens."""
        logger.info("Login: email=%s", request.data.get("email", "N/A"))
        return DRFResponse(data=kwargs["validated_data"], status=HTTP_200_OK)

    @extend_schema(
        summary="Register a new user",
        request=RegisterRequestSerializer,
        responses={
            HTTP_201_CREATED: RegisterResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(description="Rate limit exceeded"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(methods=["post"], detail=False, url_path="register", url_name="register")
    @validate_serializer_data(serializer_class=RegistrationSerializer)
    def register(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Create a new user account and return JWT tokens."""
        serializer: RegistrationSerializer = kwargs["serializer"]
        user = serializer.save()
        transaction.on_commit(lambda: send_welcome_email_task.delay(user.id))
        logger.info("Registered: user_id=%s", user.pk)
        return self.get_drf_response(
            request=request,
            data=user,
            serializer_class=RegistrationSerializer,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Refresh access token",
        request=RefreshTokenRequestSerializer,
        responses={
            HTTP_200_OK: AccessTokenResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid or expired refresh token"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(
        methods=["post"], detail=False, url_path="token/refresh", url_name="refresh"
    )
    def token_refresh(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Exchange a valid refresh token for a new access token."""
        serializer = TokenRefreshSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return DRFResponse(serializer.validated_data, status=HTTP_200_OK)
        except TokenError as exc:
            raise InvalidToken(exc.args[0])
