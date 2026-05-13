"""Views for JWT authentication (register, login, token refresh)."""

from __future__ import annotations

from typing import Any

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.abstracts.decorators import validate_serializer_data
from apps.abstracts.mixins import DRFResponseMixin
from apps.accounts.serailizers import LoginSerializer, RegistrationSerializer

logger = logging.getLogger(__name__)


class AuthViewSet(DRFResponseMixin, ViewSet):
    """Handles registration, login, and token refresh."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Obtain JWT tokens",
        request=LoginSerializer,
        responses={
            200: LoginSerializer,
            400: OpenApiResponse(description="Invalid credentials"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(methods=["post"], detail=False, url_path="token", url_name="token")
    @validate_serializer_data(serializer_class=LoginSerializer)
    def login(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Authenticate a user and return access + refresh tokens."""
        logger.info("Login: email=%s", request.data.get("email", "N/A"))
        return Response(data=kwargs["validated_data"], status=status.HTTP_200_OK)

    @extend_schema(
        summary="Register a new user",
        request=RegistrationSerializer,
        responses={
            201: RegistrationSerializer,
            400: OpenApiResponse(description="Validation error"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(methods=["post"], detail=False, url_path="register", url_name="register")
    @validate_serializer_data(serializer_class=RegistrationSerializer)
    def register(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a new user account and return JWT tokens."""
        serializer: RegistrationSerializer = kwargs["serializer"]
        user = serializer.save()
        logger.info("Registered: user_id=%s", user.pk)
        return self.get_drf_response(
            request=request,
            data=user,
            serializer_class=RegistrationSerializer,
            status_code=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Refresh access token",
        request=TokenRefreshSerializer,
        responses={
            200: TokenRefreshSerializer,
            400: OpenApiResponse(description="Invalid or expired refresh token"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(
        methods=["post"], detail=False, url_path="token/refresh", url_name="refresh"
    )
    def token_refresh(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Exchange a valid refresh token for a new access token."""
        serializer = TokenRefreshSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except TokenError as exc:
            raise InvalidToken(exc.args[0])
