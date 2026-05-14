"""Views for user/account endpoints."""

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
    HTTP_404_NOT_FOUND,
)
from rest_framework.viewsets import ViewSet

# Project modules
from apps.abstracts.decorators import require_permissions
from apps.abstracts.mixins import ViewSetWorkflowMixin
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
        responses={HTTP_200_OK: UserResponseSerializer(many=True)},
    ),
    retrieve=extend_schema(
        request=None,
        responses={
            HTTP_200_OK: UserResponseSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
        },
    ),
    create=extend_schema(
        request=UserCreateRequestSerializer,
        responses={
            HTTP_201_CREATED: UserResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
        },
    ),
    partial_update=extend_schema(
        request=UserPatchRequestSerializer,
        responses={
            HTTP_200_OK: UserResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
        },
    ),
    update=extend_schema(
        request=UserCreateRequestSerializer,
        responses={
            HTTP_200_OK: UserResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
        },
    ),
    destroy=extend_schema(
        request=None,
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(description="User deleted"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="User not found"),
        },
    ),
)
class UserViewSet(ViewSet, ViewSetWorkflowMixin):
    """ViewSet for managing user resources and profile endpoints."""

    @require_permissions(IsAdminUser)
    def list(self, request: DRFRequest) -> DRFResponse:
        """Return all users."""
        queryset = CustomUser.objects.all().order_by("id")
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=queryset,
            many=True,
            status_code=HTTP_200_OK,
        )

    @require_permissions(IsAdminUser)
    def retrieve(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Return user by primary key."""
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
        request=None,
        responses={HTTP_200_OK: UserResponseSerializer},
    )
    @action(detail=False, methods=["get"], url_path="me", url_name="me")
    @require_permissions(IsAuthenticated)
    def me(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Return the current authenticated user profile."""
        return self.serialize_to_response(
            serializer_class=UserSerializer,
            instance=request.user,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        request=UserPatchRequestSerializer,
        responses={
            HTTP_200_OK: UserResponseSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
        },
    )
    @action(detail=False, methods=["patch"], url_path="me", url_name="partial_update_me")
    @require_permissions(IsAuthenticated)
    def partial_update_me(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Partially update the current authenticated user profile."""
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
