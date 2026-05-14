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
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.viewsets import ViewSet

# Project modules
from apps.core.decorators import require_permissions
from apps.core.mixins import ViewSetWorkflowMixin
from apps.core.throttling import ActionThrottleMixin
from apps.main.models import Bookmark
from apps.main.serializers import BookmarkSerializer


logger = logging.getLogger(__name__)


class BookmarkViewSet(ActionThrottleMixin, ViewSet, ViewSetWorkflowMixin):
    """Read current user's saved articles."""

    permission_classes = [AllowAny]
    queryset = Bookmark.objects.none()

    @extend_schema(
        tags=["Bookmarks"],
        summary="List my bookmarks",
        description="Returns all bookmarks of the authenticated user, ordered by creation date. Requires authentication.",
        responses={
            HTTP_200_OK: BookmarkSerializer(many=True),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
        },
    )
    @require_permissions(IsAuthenticated)
    def list(self, request: DRFRequest) -> DRFResponse:
        """Return bookmarks for the authenticated user."""
        qs = (
            Bookmark.objects.filter(user=request.user, deleted_at__isnull=True)
            .select_related("article", "article__author", "article__category")
            .prefetch_related("article__tags")
            .order_by("-created_at")
        )
        return self.serialize_to_response(
            serializer_class=BookmarkSerializer,
            instance=qs,
            many=True,
            status_code=HTTP_200_OK,
        )
