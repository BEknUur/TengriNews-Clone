from __future__ import annotations

# Python modules
import logging

# Django modules
from django.db.models import F

# Third-party modules
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import filters
from rest_framework import serializers as drf_serializers
from rest_framework.decorators import action
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
from apps.core.mixins import DRFResponseMixin, ViewSetWorkflowMixin
from apps.core.pagination_selector import get_paginator
from apps.core.throttling import ActionThrottleMixin, throttle_scope
from apps.main.models import Article, Bookmark
from apps.main.permissions import IsAuthorOrEditorOrAdmin
from apps.main.schema_serializers import ArticleListResponseSerializer
from apps.main.serializers import (
    ArticleCreateUpdateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    BookmarkSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    ReactionSerializer,
)


logger = logging.getLogger(__name__)


class ArticleViewSet(ActionThrottleMixin, ViewSet, DRFResponseMixin, ViewSetWorkflowMixin):
    """CRUD + custom actions for news articles."""
    permission_classes = [AllowAny]
    queryset = Article.objects.none()
    serializer_class = ArticleListSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ("category", "tags", "author", "is_published")
    search_fields = ("title", "content")
    ordering_fields = ("published_at", "view_count")

    @extend_schema(
        tags=["Articles"],
        summary="List articles",
        description="Returns a paginated list of articles. Supports filtering by category, tags, author, is_published. Supports search by title and content. Supports ordering by published_at and view_count. Public endpoint.",
        responses={
            HTTP_200_OK: ArticleListResponseSerializer,
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: DRFRequest) -> DRFResponse:
        """Return a paginated list of articles."""
        qs = (
            Article.objects.select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-published_at", "-id")
        )
        paginator = get_paginator(request, self)
        return self.get_drf_response(
            request, qs, ArticleListSerializer, many=True, paginator=paginator
        )

    @extend_schema(
        tags=["Articles"],
        summary="Retrieve an article",
        description="Returns full article detail including comments and reactions. Public endpoint.",
        responses={
            HTTP_200_OK: ArticleDetailSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def retrieve(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Return full article detail."""
        obj, error_response = self.get_object_or_404_response(
            Article.objects.select_related("author", "category").prefetch_related(
                "tags", "comments", "reactions"
            ),
            pk=pk,
        )
        if error_response:
            return error_response

        return self.serialize_to_response(
            serializer_class=ArticleDetailSerializer,
            instance=obj,
            status_code=HTTP_200_OK,
            context={"request": request},
        )

    @extend_schema(
        tags=["Articles"],
        summary="Create an article",
        description="Creates a new article. Requires authentication.",
        request=ArticleCreateUpdateSerializer,
        responses={
            HTTP_201_CREATED: ArticleDetailSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @throttle_scope("article_create")
    @require_permissions(IsAuthenticated)
    def create(self, request: DRFRequest) -> DRFResponse:
        """Create a new article. Authenticated users only."""
        serializer = self.validate_request_serializer(
            ArticleCreateUpdateSerializer,
            request=request,
            context={"request": request},
        )
        article = serializer.save()
        logger.info("Article created: id=%s by user_id=%s", article.pk, request.user.pk)
        return self.serialize_to_response(
            serializer_class=ArticleDetailSerializer,
            instance=article,
            status_code=HTTP_201_CREATED,
            context={"request": request},
        )

    @extend_schema(
        tags=["Articles"],
        summary="Partially update an article",
        description="Partially updates an article. Only the article author, editor, or admin can do this.",
        request=ArticleCreateUpdateSerializer,
        responses={
            HTTP_200_OK: ArticleDetailSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def partial_update(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Partially update an article. Author, editor, or admin only."""
        obj, error_response = self.get_object_or_404_response(Article.objects, pk=pk)
        if error_response:
            return error_response
        IsAuthorOrEditorOrAdmin().check_object_permission_or_deny(request, obj)
        serializer = self.validate_request_serializer(
            ArticleCreateUpdateSerializer,
            request=request,
            instance=obj,
            partial=True,
            context={"request": request},
        )
        article = serializer.save()
        logger.info("Article updated: id=%s by user_id=%s", article.pk, request.user.pk)
        return self.serialize_to_response(
            serializer_class=ArticleDetailSerializer,
            instance=article,
            status_code=HTTP_200_OK,
            context={"request": request},
        )

    @extend_schema(
        tags=["Articles"],
        summary="Delete an article",
        description="Soft-deletes an article. Only the article author, editor, or admin can do this.",
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(description="Deleted"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    def destroy(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Soft-delete an article. Author, editor, or admin only."""
        obj, error_response = self.get_object_or_404_response(Article.objects, pk=pk)
        if error_response:
            return error_response
        IsAuthorOrEditorOrAdmin().check_object_permission_or_deny(request, obj)
        obj.delete()
        logger.info("Article soft-deleted: id=%s by user_id=%s", pk, request.user.pk)
        return DRFResponse(status=HTTP_204_NO_CONTENT)

    @extend_schema(
        tags=["Articles"],
        summary="Add a comment to an article",
        description="Adds a comment or reply to an article. Requires authentication.",
        request=CommentCreateSerializer,
        responses={
            HTTP_201_CREATED: CommentSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Article not found"),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="comments",
        permission_classes=[IsAuthenticated],
    )
    @throttle_scope("comment_create")
    def comments(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Add a comment or reply to an article."""
        article, error_response = self.get_object_or_404_response(
            Article.objects, pk=pk
        )
        if error_response:
            return error_response

        serializer = self.validate_request_serializer(
            CommentCreateSerializer,
            request=request,
            data={**request.data, "article": article.pk},
            context={"request": request},
        )
        comment = serializer.save()
        return self.serialize_to_response(
            serializer_class=CommentSerializer,
            instance=comment,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Articles"],
        summary="Add a reaction to an article",
        description="Adds a reaction to an article. Requires authentication.",
        request=ReactionSerializer,
        responses={
            HTTP_201_CREATED: ReactionSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Article not found"),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="reactions",
        permission_classes=[IsAuthenticated],
    )
    @throttle_scope("reaction")
    def reactions(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """React to an article."""
        article, error_response = self.get_object_or_404_response(
            Article.objects, pk=pk
        )
        if error_response:
            return error_response

        serializer = self.validate_request_serializer(
            ReactionSerializer,
            request=request,
            data={**request.data, "article": article.pk},
            context={"request": request},
        )
        reaction = serializer.save(user=request.user, article=article)
        return self.serialize_to_response(
            serializer_class=ReactionSerializer,
            instance=reaction,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Articles"],
        summary="Increment article view count",
        description="Increments the view counter for an article by 1. Public endpoint.",
        responses={
            HTTP_200_OK: inline_serializer("ViewCountResponse", fields={"detail": drf_serializers.CharField()}),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="view",
        permission_classes=[AllowAny],
    )
    @throttle_scope("article_view")
    def view(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Increment the view counter for an article."""
        updated = Article.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
        if not updated:
            return DRFResponse(
                {"detail": "Not found."}, status=HTTP_404_NOT_FOUND
            )
        return DRFResponse({"detail": "ok"}, status=HTTP_200_OK)

    @extend_schema(
        tags=["Articles"],
        summary="Add or remove article bookmark",
        description="POST adds a bookmark, DELETE removes it. Requires authentication.",
        responses={
            HTTP_200_OK: inline_serializer("BookmarkRemovedResponse", fields={"detail": drf_serializers.CharField()}),
            HTTP_201_CREATED: BookmarkSerializer,
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Article not found"),
        },
    )
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="bookmark",
        permission_classes=[IsAuthenticated],
    )
    @throttle_scope("bookmark")
    def bookmark(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Add or remove current user's bookmark for an article."""
        article, error_response = self.get_object_or_404_response(
            Article.objects, pk=pk
        )
        if error_response:
            return error_response

        if request.method == "DELETE":
            bookmark = Bookmark.objects.filter(
                user=request.user,
                article=article,
                deleted_at__isnull=True,
            ).first()
            if bookmark:
                bookmark.delete()
            return DRFResponse({"detail": "Bookmark removed."}, status=HTTP_200_OK)

        bookmark = Bookmark.objects.filter(user=request.user, article=article).first()

        if bookmark and bookmark.deleted_at is not None:
            bookmark.deleted_at = None
            bookmark.save(update_fields=["deleted_at", "updated_at"])
            return self.serialize_to_response(
                serializer_class=BookmarkSerializer,
                instance=bookmark,
                status_code=HTTP_201_CREATED,
            )

        if bookmark:
            return self.serialize_to_response(
                serializer_class=BookmarkSerializer,
                instance=bookmark,
                status_code=HTTP_200_OK,
            )

        bookmark = Bookmark.objects.create(user=request.user, article=article)
        return self.serialize_to_response(
            serializer_class=BookmarkSerializer,
            instance=bookmark,
            status_code=HTTP_201_CREATED,
        )
