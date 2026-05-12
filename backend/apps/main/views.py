# Python modules
from typing import Any
from django.db.models import QuerySet
from django.db import transaction

from rest_framework import status, filters
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.abstract.mixins import DRFResponseMixin
from apps.abstract.pagination_selector import get_paginator
from apps.main.models import Category, Tag, Article, Comment, Reaction
from apps.main.serializers import (
    CategorySerializer,
    TagSerializer,
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateUpdateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    ReactionSerializer,
)
from apps.main.tasks import process_article_content_task
from apps.main.permissions import (
    IsAdminOnly,
    IsAuthorOrEditorOrAdmin,
    IsCommentAuthorOrAdmin,
)


class CategoryViewSet(ViewSet):
    """ViewSet for handling Category-related endpoints."""

    queryset = Category.objects

    def get_permissions(self) -> list:
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminOnly()]

    @extend_schema(responses=CategorySerializer(many=True))
    def list(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle GET /categories/ — return all categories."""
        categories: QuerySet = self.queryset.all().order_by("name")
        serializer: CategorySerializer = CategorySerializer(categories, many=True)
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=CategorySerializer)
    def retrieve(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle GET /categories/{id}/ — return one category."""
        try:
            category: Category = self.queryset.get(pk=pk)
        except Category.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Category with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer: CategorySerializer = CategorySerializer(category)
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=CategorySerializer, responses=CategorySerializer)
    def create(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle POST /categories/ — create new category."""
        serializer: CategorySerializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=CategorySerializer, responses=CategorySerializer)
    def partial_update(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle PATCH /categories/{id}/ — partially update category."""
        try:
            category: Category = self.queryset.get(pk=pk)
        except Category.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Category with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer: CategorySerializer = CategorySerializer(
            category, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def destroy(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle DELETE /categories/{id}/ — delete category."""
        try:
            category: Category = self.queryset.get(pk=pk)
        except Category.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Category with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        category.delete()
        return DRFResponse(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ViewSet):
    """ViewSet for handling Tag-related endpoints."""

    queryset = Tag.objects

    def get_permissions(self) -> list:
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminOnly()]

    @extend_schema(responses=TagSerializer(many=True))
    def list(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle GET /tags/ — return all tags."""
        tags: QuerySet = self.queryset.all().order_by("name")
        serializer: TagSerializer = TagSerializer(tags, many=True)
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=TagSerializer)
    def retrieve(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle GET /tags/{id}/ — return one tag."""
        try:
            tag: Tag = self.queryset.get(pk=pk)
        except Tag.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Tag with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer: TagSerializer = TagSerializer(tag)
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=TagSerializer, responses=TagSerializer)
    def create(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle POST /tags/ — create new tag."""
        serializer: TagSerializer = TagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=TagSerializer, responses=TagSerializer)
    def partial_update(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle PATCH /tags/{id}/ — partially update tag."""
        try:
            tag: Tag = self.queryset.get(pk=pk)
        except Tag.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Tag with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer: TagSerializer = TagSerializer(tag, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def destroy(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle DELETE /tags/{id}/ — delete tag."""
        try:
            tag: Tag = self.queryset.get(pk=pk)
        except Tag.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Tag with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        tag.delete()
        return DRFResponse(status=status.HTTP_204_NO_CONTENT)


class ArticleViewSet(DRFResponseMixin, ViewSet):
    """ViewSet for handling Article-related endpoints."""

    queryset = Article.objects
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_fields = ("category", "tags", "author", "is_published")
    search_fields = ("title", "content")
    ordering_fields = ("published_at", "view_count")
    ordering = ("-published_at", "-id")

    def get_permissions(self) -> list:
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action in ("partial_update", "destroy"):
            return [IsAuthorOrEditorOrAdmin()]
        return [IsAuthenticated()]

    @extend_schema(
        responses=ArticleListSerializer(many=True),
        parameters=[
            OpenApiParameter(
                "pagination", OpenApiTypes.STR, description="cursor | page | limit"
            ),
            OpenApiParameter("page_size", OpenApiTypes.INT),
        ],
    )
    def list(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle GET /articles/ — return paginated articles."""
        articles: QuerySet = (
            self.queryset.all()
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-published_at", "-id")
        )
        paginator = get_paginator(request, self)
        return self.get_drf_response(
            request=request,
            data=articles,
            serializer_class=ArticleListSerializer,
            many=True,
            paginator=paginator,
        )

    @extend_schema(responses=ArticleDetailSerializer)
    def retrieve(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle GET /articles/{id}/ — return one article."""
        try:
            article: Article = (
                self.queryset.select_related("author", "category")
                .prefetch_related("tags")
                .get(pk=pk)
            )
        except Article.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Article with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer: ArticleDetailSerializer = ArticleDetailSerializer(
            article, context={"request": request}
        )
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ArticleCreateUpdateSerializer, responses=ArticleCreateUpdateSerializer
    )
    def create(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle POST /articles/ — create new article."""
        serializer: ArticleCreateUpdateSerializer = ArticleCreateUpdateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        transaction.on_commit(
            lambda: process_article_content_task.delay(serializer.instance.id)
        )
        return DRFResponse(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=ArticleCreateUpdateSerializer, responses=ArticleCreateUpdateSerializer
    )
    def partial_update(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle PATCH /articles/{id}/ — partially update article."""
        try:
            article: Article = self.queryset.get(pk=pk)
        except Article.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Article with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, article)
        serializer: ArticleCreateUpdateSerializer = ArticleCreateUpdateSerializer(
            article, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        transaction.on_commit(
            lambda: process_article_content_task.delay(serializer.instance.id)
        )

        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def destroy(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle DELETE /articles/{id}/ — delete article."""
        try:
            article: Article = self.queryset.get(pk=pk)
        except Article.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Article with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, article)
        article.delete()
        return DRFResponse(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        url_path="comments",
        permission_classes=[IsAuthenticated],
    )
    def comments(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle POST /articles/{id}/comments/ — add comment to article."""
        try:
            article: Article = self.queryset.get(pk=pk)
        except Article.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Article with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = request.data.copy()
        data["article"] = article.id
        serializer: CommentCreateSerializer = CommentCreateSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        comment: Comment = serializer.save()
        return DRFResponse(
            data=CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reactions",
        permission_classes=[IsAuthenticated],
    )
    def reactions(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle POST /articles/{id}/reactions/ — add reaction to article."""
        try:
            article: Article = self.queryset.get(pk=pk)
        except Article.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Article with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = request.data.copy()
        data["article"] = article.id
        serializer: ReactionSerializer = ReactionSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        reaction: Reaction = serializer.save()
        return DRFResponse(
            data=ReactionSerializer(reaction).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True, methods=["post"], url_path="view", permission_classes=[AllowAny]
    )
    def view(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle POST /articles/{id}/view/ — increment view count."""
        try:
            article: Article = self.queryset.get(pk=pk)
        except Article.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Article with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        article.view_count = (article.view_count or 0) + 1
        article.save(update_fields=["view_count"])
        return DRFResponse(
            data={"view_count": article.view_count},
            status=status.HTTP_200_OK,
        )


class CommentViewSet(ViewSet):
    """ViewSet for handling Comment-related endpoints."""

    queryset = Comment.objects

    def get_permissions(self) -> list:
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action in ("partial_update", "destroy"):
            return [IsCommentAuthorOrAdmin()]
        return [IsAuthenticated()]

    @extend_schema(responses=CommentSerializer(many=True))
    def list(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle GET /comments/ — return all comments."""
        comments: QuerySet = self.queryset.all().select_related("user", "article")
        serializer: CommentSerializer = CommentSerializer(comments, many=True)
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=CommentSerializer)
    def retrieve(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle GET /comments/{id}/ — return one comment."""
        try:
            comment: Comment = self.queryset.select_related("user", "article").get(
                pk=pk
            )
        except Comment.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Comment with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer: CommentSerializer = CommentSerializer(comment)
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=CommentCreateSerializer, responses=CommentSerializer)
    def create(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle POST /comments/ — create new comment."""
        serializer: CommentCreateSerializer = CommentCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    def partial_update(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle PATCH /comments/{id}/ — partially update comment."""
        try:
            comment: Comment = self.queryset.get(pk=pk)
        except Comment.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Comment with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, comment)
        serializer: CommentSerializer = CommentSerializer(
            comment, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def destroy(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle DELETE /comments/{id}/ — delete comment."""
        try:
            comment: Comment = self.queryset.get(pk=pk)
        except Comment.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Comment with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, comment)
        comment.delete()
        return DRFResponse(status=status.HTTP_204_NO_CONTENT)


class ReactionViewSet(ViewSet):
    """ViewSet for handling Reaction-related endpoints."""

    queryset = Reaction.objects

    def get_permissions(self) -> list:
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(responses=ReactionSerializer(many=True))
    def list(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle GET /reactions/ — return all reactions."""
        reactions: QuerySet = self.queryset.all().select_related(
            "user", "article", "comment"
        )
        serializer: ReactionSerializer = ReactionSerializer(reactions, many=True)
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses=ReactionSerializer)
    def retrieve(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle GET /reactions/{id}/ — return one reaction."""
        try:
            reaction: Reaction = self.queryset.select_related(
                "user", "article", "comment"
            ).get(pk=pk)
        except Reaction.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Reaction with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer: ReactionSerializer = ReactionSerializer(reaction)
        return DRFResponse(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ReactionSerializer, responses=ReactionSerializer)
    def create(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """Handle POST /reactions/ — create new reaction."""
        serializer: ReactionSerializer = ReactionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={204: None})
    def destroy(
        self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any
    ) -> DRFResponse:
        """Handle DELETE /reactions/{id}/ — delete reaction."""
        try:
            reaction: Reaction = self.queryset.get(pk=pk)
        except Reaction.DoesNotExist:
            return DRFResponse(
                data={"id": [f"Reaction with id={pk} does not exist."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        reaction.delete()
        return DRFResponse(status=status.HTTP_204_NO_CONTENT)
