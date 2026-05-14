"""Views for user profile management."""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.viewsets import ViewSet

# project modules
from apps.abstracts.decorators import require_permissions
from apps.abstracts.mixins import ViewSetWorkflowMixin
from apps.accounts.models import CustomUser
from apps.accounts.serailizers import UserSerializer, UserUpdateSerializer


class UserViewSet(ViewSet, ViewSetWorkflowMixin):
    """CRUD for user accounts (admin-facing) and self-service profile."""

    @extend_schema(
        summary="List all users",
        responses={
            HTTP_200_OK: UserSerializer(many=True),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAdminUser)
    def list(self, request: DRFRequest) -> DRFResponse:
        """Return all users. Admin only."""
        qs = CustomUser.objects.all().order_by("id")
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=qs,
            many=True,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        summary="Retrieve a single user",
        responses={
            HTTP_200_OK: UserSerializer,
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAdminUser)
    def retrieve(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Return a single user by primary key. Admin only."""
        user, error_response = self.get_object_or_404_response(CustomUser.objects, pk=pk)
        if error_response:
            return error_response
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=user,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        summary="Current user profile",
        responses={
            HTTP_200_OK: UserSerializer,
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request: DRFRequest) -> DRFResponse:
        """Return the profile of the currently authenticated user."""
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=request.user,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        summary="Update current user profile",
        request=UserUpdateSerializer,
        responses={
            HTTP_200_OK: UserSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(
        detail=False,
        methods=["patch"],
        url_path="me/update",
        permission_classes=[IsAuthenticated],
    )
    def partial_update_me(self, request: DRFRequest) -> DRFResponse:
        """Partially update the profile of the currently authenticated user."""
        serializer = self.validate_request_serializer(
            UserUpdateSerializer,
            request=request,
            instance=request.user,
            partial=True,
        )
        serializer.save()
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=request.user,
            status_code=HTTP_200_OK,
        )
