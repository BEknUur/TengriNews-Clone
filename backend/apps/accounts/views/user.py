from __future__ import annotations

# Python modules
from typing import Any

# Third-party modules
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.viewsets import ViewSet

# Project modules
from apps.core.decorators import require_permissions
from apps.core.mixins import ViewSetWorkflowMixin
from apps.core.throttling import ActionThrottleMixin
from apps.accounts.models import CustomUser
from apps.accounts.serializers.schema_serializers import (
    UserCreateRequestSerializer,
    UserPatchRequestSerializer,
    UserResponseSerializer,
)
from apps.accounts.serializers.serializers import UserSerializer, UserUpdateSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Users"],
        summary="List all users",
        description="Returns all users ordered by ID. Admin only.",
        request=None,
        responses={
            HTTP_200_OK: UserResponseSerializer(many=True),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    ),
    retrieve=extend_schema(
        tags=["Users"],
        summary="Retrieve a user",
        description="Returns a single user by ID. Admin only.",
        request=None,
        responses={
            HTTP_200_OK: UserResponseSerializer,
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    ),
    create=extend_schema(
        tags=["Users"],
        summary="Create a user",
        description="Creates a new user account. Requires authentication.",
        request=UserCreateRequestSerializer,
        responses={
            HTTP_201_CREATED: UserResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    ),
    partial_update=extend_schema(
        tags=["Users"],
        summary="Partially update a user",
        description="Partially updates a user. Requires authentication.",
        request=UserPatchRequestSerializer,
        responses={
            HTTP_200_OK: UserResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    ),
    update=extend_schema(
        tags=["Users"],
        summary="Fully update a user",
        description="Fully replaces a user's data. Requires authentication.",
        request=UserCreateRequestSerializer,
        responses={
            HTTP_200_OK: UserResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    ),
    destroy=extend_schema(
        tags=["Users"],
        summary="Delete a user",
        description="Permanently deletes a user account. Requires authentication.",
        request=None,
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(description="User deleted"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    ),
)
class UserViewSet(ActionThrottleMixin, ViewSet, ViewSetWorkflowMixin):
    """CRUD for user accounts (admin-facing) and self-service profile."""
    queryset = CustomUser.objects.none()
    serializer_class = UserSerializer

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

    @require_permissions(IsAuthenticated)
    def create(self, request: DRFRequest) -> DRFResponse:
        """Create a user."""
        serializer = self.validate_request_serializer(
            UserSerializer,
            request=request,
        )
        user = serializer.save()
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=user,
            status_code=HTTP_201_CREATED,
        )

    @require_permissions(IsAuthenticated)
    def partial_update(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Partially update a user."""
        user, error_response = self.get_object_or_404_response(CustomUser.objects, pk=pk)
        if error_response:
            return error_response

        serializer = self.validate_request_serializer(
            UserSerializer,
            request=request,
            instance=user,
            partial=True,
        )
        serializer.save()
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=user,
            status_code=HTTP_200_OK,
        )

    @require_permissions(IsAuthenticated)
    def update(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Fully update a user."""
        user, error_response = self.get_object_or_404_response(CustomUser.objects, pk=pk)
        if error_response:
            return error_response

        serializer = self.validate_request_serializer(
            UserSerializer,
            request=request,
            instance=user,
            partial=False,
        )
        serializer.save()
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=user,
            status_code=HTTP_200_OK,
        )

    @require_permissions(IsAuthenticated)
    def destroy(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Delete a user."""
        user, error_response = self.get_object_or_404_response(CustomUser.objects, pk=pk)
        if error_response:
            return error_response

        user.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)

    @extend_schema(
        tags=["Users"],
        summary="Current user profile",
        description="Returns the profile of the currently authenticated user.",
        request=None,
        responses={
            HTTP_200_OK: UserResponseSerializer,
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
    def me(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Return the profile of the currently authenticated user."""
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=request.user,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Users"],
        summary="Update current user profile",
        description="Updates the profile fields (first_name, last_name, avatar) of the currently authenticated user.",
        request=UserPatchRequestSerializer,
        responses={
            HTTP_200_OK: UserResponseSerializer,
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
    def partial_update_me(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
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
