"""Views for user profile management."""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

# project modules
from apps.accounts.models import CustomUser
from apps.accounts.serailizers import UserSerializer, UserUpdateSerializer


class UserViewSet(ViewSet):
    """CRUD for user accounts (admin-facing) and self-service profile."""

    @extend_schema(
        summary="List all users",
        responses={
            200: UserSerializer(many=True),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: Request) -> Response:
        """Return all users. Admin only."""
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        qs = CustomUser.objects.all().order_by("id")
        return Response(UserSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Retrieve a single user",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """Return a single user by primary key. Admin only."""
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Current user profile",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Unauthorized"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request: Request) -> Response:
        """Return the profile of the currently authenticated user."""
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update current user profile",
        request=UserUpdateSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    @action(
        detail=False,
        methods=["patch"],
        url_path="me/update",
        permission_classes=[IsAuthenticated],
    )
    def partial_update_me(self, request: Request) -> Response:
        """Partially update the profile of the currently authenticated user."""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
