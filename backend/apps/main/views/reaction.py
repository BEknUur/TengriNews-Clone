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
from apps.main.models import Reaction
from apps.main.serializers import ReactionSerializer


logger = logging.getLogger(__name__)


class ReactionViewSet(ActionThrottleMixin, ViewSet, ViewSetWorkflowMixin):
    """CRUD operations for reactions."""
    permission_classes = [AllowAny]
    queryset = Reaction.objects.none()

    @extend_schema(
        tags=["Reactions"],
        summary="List all reactions",
        description="Returns all reactions. Public endpoint.",
        responses={
            HTTP_200_OK: ReactionSerializer(many=True),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: DRFRequest) -> DRFResponse:
        """Return all reactions."""
        qs = Reaction.objects.select_related("user", "article", "comment")
        return self.serialize_to_response(
            serializer_class=ReactionSerializer,
            instance=qs,
            many=True,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Reactions"],
        summary="Retrieve a reaction",
        description="Returns a single reaction by ID. Public endpoint.",
        responses={
            HTTP_200_OK: ReactionSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def retrieve(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Return a single reaction by primary key."""
        obj, error_response = self.get_object_or_404_response(Reaction.objects, pk=pk)
        if error_response:
            return error_response

        return self.serialize_to_response(
            serializer_class=ReactionSerializer,
            instance=obj,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        tags=["Reactions"],
        summary="Create a reaction",
        description="Creates a reaction on an article or comment. Requires authentication.",
        request=ReactionSerializer,
        responses={
            HTTP_201_CREATED: ReactionSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @throttle_scope("reaction")
    @require_permissions(IsAuthenticated)
    def create(self, request: DRFRequest) -> DRFResponse:
        """Create a reaction. Authenticated users only."""
        serializer = self.validate_request_serializer(
            ReactionSerializer,
            request=request,
            context={"request": request},
        )
        reaction = serializer.save(user=request.user)
        return self.serialize_to_response(
            serializer_class=ReactionSerializer,
            instance=reaction,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Reactions"],
        summary="Delete a reaction",
        description="Deletes a reaction. Only the reaction owner can do this.",
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(description="Deleted"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAuthenticated)
    def destroy(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Delete a reaction. Reaction owner only."""
        obj, error_response = self.get_object_or_404_response(Reaction.objects, pk=pk)
        if error_response:
            return error_response

        if obj.user_id != request.user.pk:
            return DRFResponse(
                {"detail": "Forbidden."}, status=HTTP_403_FORBIDDEN
            )
        obj.delete()
        logger.info('Reaction deleted: id=%s by user_id=%s', pk, request.user.pk)
        return DRFResponse(status=HTTP_204_NO_CONTENT)
