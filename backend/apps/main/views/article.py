from __future__ import annotations

# Django modules
from django.db.models import F

# Third-party modules
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import filters
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
from apps.main.models import Article, Bookmark
from apps.main.permissions import IsAuthorOrEditorOrAdmin
from apps.main.serializers import (
    ArticleCreateUpdateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    BookmarkSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    ReactionSerializer,
)


class ArticleViewSet(ViewSet, DRFResponseMixin, ViewSetWorkflowMixin):
    """CRUD + custom actions for news articles."""
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ("category", "tags", "author", "is_published")
    search_fields = ("title", "content")
    ordering_fields = ("published_at", "view_count")

    @extend_schema(
        summary="List articles",
        responses={
            HTTP_200_OK: ArticleListSerializer(many=True),
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
        summary="Retrieve an article",
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
        summary="Create an article",
        request=ArticleCreateUpdateSerializer,
        responses={
            HTTP_201_CREATED: ArticleDetailSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAuthenticated)
    def create(self, request: DRFRequest) -> DRFResponse:
        """Create a new article. Authenticated users only."""
        serializer = self.validate_request_serializer(
            ArticleCreateUpdateSerializer,
            request=request,
            context={"request": request},
        )
        article = serializer.save()
        return self.serialize_to_response(
            serializer_class=ArticleDetailSerializer,
            instance=article,
            status_code=HTTP_201_CREATED,
            context={"request": request},
        )

    @extend_schema(
        summary="Partially update an article",
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
        return self.serialize_to_response(
            serializer_class=ArticleDetailSerializer,
            instance=article,
            status_code=HTTP_200_OK,
            context={"request": request},
        )

    @extend_schema(
        summary="Delete an article",
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
        return DRFResponse(status=HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Add a comment to an article",
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
        summary="Add a reaction to an article",
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
        summary="Increment article view count",
        responses={
            HTTP_200_OK: OpenApiResponse(description="view_count incremented"),
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="view",
        permission_classes=[AllowAny],
    )
    def view(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Increment the view counter for an article."""
        updated = Article.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
        if not updated:
            return DRFResponse(
                {"detail": "Not found."}, status=HTTP_404_NOT_FOUND
            )
        return DRFResponse({"detail": "ok"}, status=HTTP_200_OK)

    @extend_schema(
        summary="Add or remove article bookmark",
        responses={
            HTTP_200_OK: BookmarkSerializer,
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
