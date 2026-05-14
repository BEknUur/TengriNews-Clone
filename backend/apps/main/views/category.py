from __future__ import annotations

# Python modules
import logging

# Third-party modules
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny
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
from apps.main.models import Category
from apps.main.permissions import IsAdminOnly
from apps.main.serializers import CategorySerializer


logger = logging.getLogger(__name__)


class CategoryViewSet(ActionThrottleMixin, ViewSet, ViewSetWorkflowMixin):
    """CRUD operations for article categories."""
    permission_classes = [AllowAny]
    queryset = Category.objects.none()

    @extend_schema(
        tags=["Categories"],
        summary="List all categories",
        description="Returns all categories. Public endpoint.",
        responses={
            HTTP_200_OK: CategorySerializer(many=True),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: DRFRequest) -> DRFResponse:
        """Return all categories ordered by name."""
        qs = Category.objects.all()
        return self.serialize_to_response(
            serializer_class=CategorySerializer,
            instance=qs,
            many=True,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Categories"],
        summary="Retrieve a category",
        description="Returns a single category by ID. Public endpoint.",
        responses={
            HTTP_200_OK: CategorySerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                description="Internal server error"
            ),
        },
    )
    def retrieve(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Return a single category by primary key."""
        obj, error_response = self.get_object_or_404_response(Category.objects, pk=pk)
        if error_response:
            return error_response

        return self.serialize_to_response(
            serializer_class=CategorySerializer,
            instance=obj,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Categories"],
        summary="Create a category",
        description="Creates a new category. Admin only.",
        request=CategorySerializer,
        responses={
            HTTP_201_CREATED: CategorySerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden — admin only"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAdminOnly)
    def create(self, request: DRFRequest) -> DRFResponse:
        """Create a new category. Admin only."""
        serializer = self.validate_request_serializer(
            CategorySerializer,
            request=request,
        )
        category = serializer.save()
        logger.info('Category created: id=%s by user_id=%s', category.pk, request.user.pk)
        return self.serialize_to_response(
            serializer_class=CategorySerializer,
            instance=category,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Categories"],
        summary="Partially update a category",
        description="Partially updates an existing category. Admin only.",
        request=CategorySerializer,
        responses={
            HTTP_200_OK: CategorySerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden — admin only"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAdminOnly)
    def partial_update(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Partially update an existing category. Admin only."""
        obj, error_response = self.get_object_or_404_response(Category.objects, pk=pk)
        if error_response:
            return error_response

        serializer = self.validate_request_serializer(
            CategorySerializer,
            request=request,
            instance=obj,
            partial=True,
        )
        category = serializer.save()
        logger.info('Category updated: id=%s by user_id=%s', category.pk, request.user.pk)
        return self.serialize_to_response(
            serializer_class=CategorySerializer,
            instance=category,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Categories"],
        summary="Delete a category",
        description="Deletes a category permanently. Admin only.",
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(description="Deleted"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden — admin only"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAdminOnly)
    def destroy(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Delete a category. Admin only."""
        obj, error_response = self.get_object_or_404_response(Category.objects, pk=pk)
        if error_response:
            return error_response

        obj.delete()
        logger.info('Category deleted: id=%s by user_id=%s', pk, request.user.pk)
        return DRFResponse(status=HTTP_204_NO_CONTENT)
