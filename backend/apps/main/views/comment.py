from __future__ import annotations

# Python modules
import logging

# Third-party modules
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
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
from apps.core.throttling import ActionThrottleMixin, throttle_scope
from apps.main.models import Comment
from apps.main.permissions import IsCommentAuthorOrAdmin
from apps.main.serializers import CommentCreateSerializer, CommentSerializer


logger = logging.getLogger(__name__)


class CommentViewSet(ActionThrottleMixin, ViewSet, ViewSetWorkflowMixin):
    """CRUD operations for comments."""
    permission_classes = [AllowAny]
    queryset = Comment.objects.none()

    @extend_schema(
        tags=["Comments"],
        summary="List all comments",
        description="Returns all active comments ordered by creation date. Public endpoint.",
        responses={
            HTTP_200_OK: CommentSerializer(many=True),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: DRFRequest) -> DRFResponse:
        """Return all active comments."""
        qs = (
            Comment.objects.filter(is_active=True)
            .select_related("user")
            .order_by("created_at")
        )
        return self.serialize_to_response(
            serializer_class=CommentSerializer,
            instance=qs,
            many=True,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Comments"],
        summary="Retrieve a comment",
        description="Returns a single active comment by ID. Public endpoint.",
        responses={
            HTTP_200_OK: CommentSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def retrieve(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Return a single comment by primary key."""
        obj, error_response = self.get_object_or_404_response(
            Comment.objects,
            pk=pk,
            is_active=True,
        )
        if error_response:
            return error_response

        return self.serialize_to_response(
            serializer_class=CommentSerializer,
            instance=obj,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Comments"],
        summary="Create a comment",
        description="Creates a new comment. Requires authentication.",
        request=CommentCreateSerializer,
        responses={
            HTTP_201_CREATED: CommentSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @throttle_scope("comment_create")
    @require_permissions(IsAuthenticated)
    def create(self, request: DRFRequest) -> DRFResponse:
        """Create a new comment. Authenticated users only."""
        serializer = self.validate_request_serializer(
            CommentCreateSerializer,
            request=request,
            context={"request": request},
        )
        comment = serializer.save()
        logger.info('Comment created: id=%s by user_id=%s', comment.pk, request.user.pk)
        return self.serialize_to_response(
            serializer_class=CommentSerializer,
            instance=comment,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Comments"],
        summary="Partially update a comment",
        description="Partially updates a comment. Only the comment author or admin can do this.",
        request=CommentCreateSerializer,
        responses={
            HTTP_200_OK: CommentSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def partial_update(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Partially update a comment. Author or admin only."""
        obj, error_response = self.get_object_or_404_response(Comment.objects, pk=pk)
        if error_response:
            return error_response

        IsCommentAuthorOrAdmin().check_object_permission_or_deny(request, obj)
        serializer = self.validate_request_serializer(
            CommentCreateSerializer,
            request=request,
            instance=obj,
            partial=True,
            context={"request": request},
        )
        comment = serializer.save()
        logger.info('Comment updated: id=%s by user_id=%s', comment.pk, request.user.pk)
        return self.serialize_to_response(
            serializer_class=CommentSerializer,
            instance=comment,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Comments"],
        summary="Delete a comment",
        description="Soft-deletes a comment. Only the comment author or admin can do this.",
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(description="Deleted"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def destroy(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Soft-delete a comment. Author or admin only."""
        obj, error_response = self.get_object_or_404_response(Comment.objects, pk=pk)
        if error_response:
            return error_response

        IsCommentAuthorOrAdmin().check_object_permission_or_deny(request, obj)
        obj.delete()
        logger.info('Comment soft-deleted: id=%s by user_id=%s', pk, request.user.pk)
        return DRFResponse(status=HTTP_204_NO_CONTENT)
