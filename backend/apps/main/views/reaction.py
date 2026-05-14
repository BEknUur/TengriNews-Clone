from __future__ import annotations

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
from apps.main.models import Reaction
from apps.main.serializers import ReactionSerializer


class ReactionViewSet(ViewSet, ViewSetWorkflowMixin):
    """CRUD operations for reactions."""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List all reactions",
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
        summary="Retrieve a reaction",
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
        summary="Create a reaction",
        request=ReactionSerializer,
        responses={
            HTTP_201_CREATED: ReactionSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
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
        summary="Delete a reaction",
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
        return DRFResponse(status=HTTP_204_NO_CONTENT)
