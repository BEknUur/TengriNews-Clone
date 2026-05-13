"""Views for user/account endpoints."""

# Python modules
from typing import Any

# Third-party modules
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse

# Project modules
from apps.accounts.models import CustomUser
from apps.accounts.schema_serializers import (
    UserCreateRequestSerializer,
    UserPatchRequestSerializer,
    UserResponseSerializer,
)
from apps.accounts.serializers import UserSerializer, UserUpdateSerializer


@extend_schema_view(
    list=extend_schema(
        request=None,
        responses={status.HTTP_200_OK: UserResponseSerializer(many=True)},
    ),
    retrieve=extend_schema(
        request=None,
        responses={
            status.HTTP_200_OK: UserResponseSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
        },
    ),
    create=extend_schema(
        request=UserCreateRequestSerializer,
        responses={
            status.HTTP_201_CREATED: UserResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
        },
    ),
    partial_update=extend_schema(
        request=UserPatchRequestSerializer,
        responses={
            status.HTTP_200_OK: UserResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
        },
    ),
    update=extend_schema(
        request=UserCreateRequestSerializer,
        responses={
            status.HTTP_200_OK: UserResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
        },
    ),
    destroy=extend_schema(
        request=None,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="User deleted"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
        },
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user resources and profile endpoints."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self) -> list[BasePermission]:
        """Return permissions depending on the current action."""
        if self.action in ("list", "retrieve"):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @extend_schema(
        request=None,
        responses={status.HTTP_200_OK: UserResponseSerializer},
    )
    @action(detail=False, methods=["get"], url_path="me", url_name="me")
    def me(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Return the current authenticated user profile."""
        serializer: UserSerializer = UserSerializer(request.user)
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserPatchRequestSerializer,
        responses={
            status.HTTP_200_OK: UserResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
        },
    )
    @action(detail=False, methods=["patch"], url_path="me", url_name="partial_update_me")
    def partial_update_me(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Partially update the current authenticated user profile."""
        serializer: UserUpdateSerializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(
            data=UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )
