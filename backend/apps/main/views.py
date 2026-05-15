"""ViewSets for categories, tags, articles, comments, and reactions."""

from __future__ import annotations

# Python modules

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
from apps.abstracts.decorators import require_permissions
from apps.abstracts.mixins import DRFResponseMixin, ViewSetWorkflowMixin
from apps.abstracts.pagination_selector import get_paginator
from apps.main.models import Article, Bookmark, Category, Comment, Reaction, Tag
from apps.main.permissions import (
    IsAdminOnly,
    IsAuthorOrEditorOrAdmin,
    IsCommentAuthorOrAdmin,
)
from apps.main.serializers import (
    ArticleCreateUpdateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    BookmarkSerializer,
    CategorySerializer,
    CommentCreateSerializer,
    CommentSerializer,
    ReactionSerializer,
    TagSerializer,
)
from django.conf import settings
from apps.main.utils.cache import make_article_detail_key, cache_get, cache_set
from apps.main.utils.cache import make_article_list_key, get_list_version


class CategoryViewSet(ViewSet, ViewSetWorkflowMixin):
    """CRUD operations for article categories."""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List all categories",
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
        summary="Retrieve a category",
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
        summary="Create a category",
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
        return self.serialize_to_response(
            serializer_class=CategorySerializer,
            instance=category,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Partially update a category",
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
        return self.serialize_to_response(
            serializer_class=CategorySerializer,
            instance=category,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a category",
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
        return DRFResponse(status=HTTP_204_NO_CONTENT)


class TagViewSet(ViewSet, ViewSetWorkflowMixin):
    """CRUD operations for article tags."""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List all tags",
        responses={
            HTTP_200_OK: TagSerializer(many=True),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
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
        summary="Retrieve a tag",
        responses={
            HTTP_200_OK: TagSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(description="Not found"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
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
        summary="Create a tag",
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
        return self.serialize_to_response(
            serializer_class=TagSerializer,
            instance=tag,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Partially update a tag",
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
        return self.serialize_to_response(
            serializer_class=TagSerializer,
            instance=tag,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a tag",
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
        return DRFResponse(status=HTTP_204_NO_CONTENT)


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
        # try list cache first
        params: dict = {}
        for k in sorted(request.GET.keys()):
            vals = request.GET.getlist(k)
            params[k] = ",".join(vals)

        try:
            list_key = make_article_list_key(params)
            cached = None
            try:
                cached = cache_get(list_key)
            except Exception:
                cached = None
            if cached is not None:
                return DRFResponse(data=cached, status=HTTP_200_OK)
        except Exception:
            list_key = None

        qs = (
            Article.objects.select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-published_at", "-id")
        )
        paginator = get_paginator(request, self)
        response = self.get_drf_response(
            request, qs, ArticleListSerializer, many=True, paginator=paginator
        )

        # cache paginated response data
        if list_key is not None and response.status_code == HTTP_200_OK:
            try:
                ttl = getattr(settings, "ARTICLE_LIST_TTL", 60)
                cache_set(list_key, response.data, ttl)
            except Exception:
                pass

        return response

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
        # try cache first
        try:
            key = make_article_detail_key(int(pk)) if pk is not None else None
        except Exception:
            key = None

        if key:
            try:
                cached = cache_get(key)
                if cached is not None:
                    return DRFResponse(data=cached, status=HTTP_200_OK)
            except Exception:
                # don't fail the whole request on cache errors
                pass

        obj, error_response = self.get_object_or_404_response(
            Article.objects.select_related("author", "category").prefetch_related(
                "tags", "comments", "reactions"
            ),
            pk=pk,
        )
        if error_response:
            return error_response

        # serialize and store in cache
        serializer = ArticleDetailSerializer(obj, context={"request": request})
        data = serializer.data
        ttl = getattr(settings, "ARTICLE_DETAIL_TTL", 300)
        if key:
            try:
                cache_set(key, data, ttl)
            except Exception:
                pass

        return DRFResponse(data=data, status=HTTP_200_OK)

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
        self.check_permissions(request)
        serializer = ArticleCreateUpdateSerializer(
            data=request.data, context={"request": request}
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

        # Explicitly pass scalar `type` and the article id to avoid QueryDict lists
        raw_type = request.data.get("type")
        if isinstance(raw_type, (list, tuple)):
            raw_type = raw_type[0] if raw_type else None
        pythondata = {
            "type": raw_type,
            "article": article.pk,
        }
        serializer = self.validate_request_serializer(
            ReactionSerializer,
            request=request,
            data=pythondata,
            context={"request": request},
        )
        reaction = serializer.save(user=request.user)
        return self.serialize_to_response(
            serializer_class=ReactionSerializer,
            instance=reaction,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Add a reaction to an article (compat)",
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
        url_path="react",
        permission_classes=[IsAuthenticated],
    )
    def react(self, request: DRFRequest, pk: str | None = None) -> DRFResponse:
        """Compatibility wrapper for `/react/` URL used in tests."""
        return self.reactions(request, pk=pk)

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

            return DRFResponse(
                {"detail": "Bookmark removed."}, status=HTTP_200_OK
            )

        bookmark = Bookmark.objects.filter(
            user=request.user,
            article=article,
        ).first()

        if bookmark and bookmark.deleted_at is not None:
            bookmark.deleted_at = None
            bookmark.save(update_fields=["deleted_at", "updated_at"])
            return DRFResponse(
                BookmarkSerializer(bookmark).data,
                status=HTTP_201_CREATED,
            )

        if bookmark:
            return DRFResponse(
                BookmarkSerializer(bookmark).data,
                status=HTTP_200_OK,
            )

        bookmark = Bookmark.objects.create(user=request.user, article=article)
        return DRFResponse(
            BookmarkSerializer(bookmark).data,
            status=HTTP_201_CREATED,
        )


class CommentViewSet(ViewSet, ViewSetWorkflowMixin):
    """CRUD operations for comments."""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List all comments",
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
        summary="Retrieve a comment",
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
        summary="Create a comment",
        request=CommentCreateSerializer,
        responses={
            HTTP_201_CREATED: CommentSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(description="Validation error"),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized"),
            HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        },
    )
    @require_permissions(IsAuthenticated)
    def create(self, request: DRFRequest) -> DRFResponse:
        """Create a new comment. Authenticated users only."""
        IsAuthenticated().check_permission_or_deny(request)
        serializer = CommentCreateSerializer(
            data=request.data, context={"request": request}
        )
        comment = serializer.save()
        return self.serialize_to_response(
            serializer_class=CommentSerializer,
            instance=comment,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Partially update a comment",
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
        return self.serialize_to_response(
            serializer_class=CommentSerializer,
            instance=comment,
            status_code=HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a comment",
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
        return DRFResponse(status=HTTP_204_NO_CONTENT)


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
        IsAuthenticated().check_permission_or_deny(request)
        serializer = ReactionSerializer(
            data=request.data, context={"request": request}
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
        IsAuthenticated().check_permission_or_deny(request)
        try:
            obj = Reaction.objects.get(pk=pk)
        except Reaction.DoesNotExist:
            return DRFResponse({"detail": "Not found."}, status=HTTP_404_NOT_FOUND)
        if obj.user_id != request.user.pk:
            return DRFResponse(
                {"detail": "Forbidden."}, status=HTTP_403_FORBIDDEN
            )
        obj.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


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
        IsAuthenticated().check_permission_or_deny(request)
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
