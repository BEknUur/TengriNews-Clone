from __future__ import annotations

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
from apps.main.models import Bookmark
from apps.main.serializers import BookmarkSerializer


class BookmarkViewSet(ViewSet, ViewSetWorkflowMixin):
    """Read current user's saved articles."""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List my bookmarks",
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
