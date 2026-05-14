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
from apps.core.cache import cache_response
from apps.core.decorators import require_permissions
from apps.core.mixins import ViewSetWorkflowMixin
from apps.core.throttling import ActionThrottleMixin
from apps.main.models import Tag
from apps.main.permissions import IsAdminOnly
from apps.main.serializers import TagSerializer


logger = logging.getLogger(__name__)


class TagViewSet(ActionThrottleMixin, ViewSet, ViewSetWorkflowMixin):
    """CRUD operations for article tags."""
    permission_classes = [AllowAny]
    queryset = Tag.objects.none()

    @extend_schema(
        tags=["Tags"],
        summary="List all tags",
        description="Returns all tags. Public endpoint.",
        responses={
            HTTP_200_OK: TagSerializer(many=True),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @cache_response(timeout=600, namespace="tags")
    def list(self, request: DRFRequest) -> DRFResponse:
        """Return all tags ordered by name."""
        qs = Tag.objects.all()
        return self.serialize_to_response(
            serializer_class=TagSerializer,
            instance=qs,
            many=True,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Tags"],
        summary="Retrieve a tag",
        description="Returns a single tag by ID. Public endpoint.",
        responses={
            HTTP_200_OK: TagSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @cache_response(timeout=600, namespace="tags")
    def retrieve(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Return a single tag by primary key."""
        obj, error_response = self.get_object_or_404_response(Tag.objects, pk=pk)
        if error_response:
            return error_response

        return self.serialize_to_response(
            serializer_class=TagSerializer,
            instance=obj,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Tags"],
        summary="Create a tag",
        description="Creates a new tag. Admin only.",
        request=TagSerializer,
        responses={
            HTTP_201_CREATED: TagSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden — admin only"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAdminOnly)
    def create(self, request: DRFRequest) -> DRFResponse:
        """Create a new tag. Admin only."""
        serializer = self.validate_request_serializer(
            TagSerializer,
            request=request,
        )
        tag = serializer.save()
        logger.info('Tag created: id=%s by user_id=%s', tag.pk, request.user.pk)
        return self.serialize_to_response(
            serializer_class=TagSerializer,
            instance=tag,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Tags"],
        summary="Partially update a tag",
        description="Partially updates an existing tag. Admin only.",
        request=TagSerializer,
        responses={
            HTTP_200_OK: TagSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden — admin only"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAdminOnly)
    def partial_update(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Partially update an existing tag. Admin only."""
        obj, error_response = self.get_object_or_404_response(Tag.objects, pk=pk)
        if error_response:
            return error_response

        serializer = self.validate_request_serializer(
            TagSerializer,
            request=request,
            instance=obj,
            partial=True,
        )
        tag = serializer.save()
        logger.info('Tag updated: id=%s by user_id=%s', tag.pk, request.user.pk)
        return self.serialize_to_response(
            serializer_class=TagSerializer,
            instance=tag,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Tags"],
        summary="Delete a tag",
        description="Deletes a tag permanently. Admin only.",
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
        """Delete a tag. Admin only."""
        obj, error_response = self.get_object_or_404_response(Tag.objects, pk=pk)
        if error_response:
            return error_response

        obj.delete()
        logger.info('Tag deleted: id=%s by user_id=%s', pk, request.user.pk)
        return DRFResponse(status=HTTP_204_NO_CONTENT)
