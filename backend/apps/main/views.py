"""ViewSets for categories, tags, articles, comments, and reactions."""
from __future__ import annotations

# Python modules
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.abstracts.mixins import DRFResponseMixin
from apps.abstracts.pagination_selector import get_paginator
from apps.main.models import Article, Category, Comment, Reaction, Tag
from apps.main.permissions import (
    IsAdminOnly,
    IsAuthorOrEditorOrAdmin,
    IsCommentAuthorOrAdmin,
)
from apps.main.serializers import (
    ArticleCreateUpdateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    CategorySerializer,
    CommentCreateSerializer,
    CommentSerializer,
    ReactionSerializer,
    TagSerializer,
)


class CategoryViewSet(ViewSet):
    """CRUD operations for article categories."""

    @extend_schema(
        summary="List all categories",
        responses={
            200: CategorySerializer(many=True),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: Request) -> Response:
        """Return all categories ordered by name."""
        qs = Category.objects.all()
        return Response(
            CategorySerializer(qs, many=True).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Retrieve a category",
        responses={
            200: CategorySerializer,
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """Return a single category by primary key."""
        try:
            obj = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(CategorySerializer(obj).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a category",
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden — admin only"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def create(self, request: Request) -> Response:
        """Create a new category. Admin only."""
        IsAdminOnly().check_permission_or_deny(request)
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Partially update a category",
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden — admin only"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def partial_update(self, request: Request, pk: str | None = None) -> Response:
        """Partially update an existing category. Admin only."""
        IsAdminOnly().check_permission_or_deny(request)
        try:
            obj = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a category",
        responses={
            204: OpenApiResponse(description="Deleted"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden — admin only"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def destroy(self, request: Request, pk: str | None = None) -> Response:
        """Delete a category. Admin only."""
        IsAdminOnly().check_permission_or_deny(request)
        try:
            obj = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ViewSet):
    """CRUD operations for article tags."""

    @extend_schema(
        summary="List all tags",
        responses={
            200: TagSerializer(many=True),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: Request) -> Response:
        """Return all tags ordered by name."""
        qs = Tag.objects.all()
        return Response(TagSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Retrieve a tag",
        responses={
            200: TagSerializer,
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """Return a single tag by primary key."""
        try:
            obj = Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(TagSerializer(obj).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a tag",
        request=TagSerializer,
        responses={
            201: TagSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden — admin only"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def create(self, request: Request) -> Response:
        """Create a new tag. Admin only."""
        IsAdminOnly().check_permission_or_deny(request)
        serializer = TagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Partially update a tag",
        request=TagSerializer,
        responses={
            200: TagSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden — admin only"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def partial_update(self, request: Request, pk: str | None = None) -> Response:
        """Partially update an existing tag. Admin only."""
        IsAdminOnly().check_permission_or_deny(request)
        try:
            obj = Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TagSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a tag",
        responses={
            204: OpenApiResponse(description="Deleted"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden — admin only"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def destroy(self, request: Request, pk: str | None = None) -> Response:
        """Delete a tag. Admin only."""
        IsAdminOnly().check_permission_or_deny(request)
        try:
            obj = Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArticleViewSet(ViewSet, DRFResponseMixin):
    """CRUD + custom actions for news articles."""

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "tags", "author", "is_published"]
    search_fields = ["title", "content"]
    ordering_fields = ["published_at", "view_count"]

    @extend_schema(
        summary="List articles",
        responses={
            200: ArticleListSerializer(many=True),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: Request) -> Response:
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
            200: ArticleDetailSerializer,
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """Return full article detail."""
        try:
            obj = (
                Article.objects.select_related("author", "category")
                .prefetch_related("tags", "comments", "reactions")
                .get(pk=pk)
            )
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            ArticleDetailSerializer(obj, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Create an article",
        request=ArticleCreateUpdateSerializer,
        responses={
            201: ArticleDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def create(self, request: Request) -> Response:
        """Create a new article. Authenticated users only."""
        IsAuthenticated().check_permission_or_deny(request)
        serializer = ArticleCreateUpdateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        article = serializer.save()
        return Response(
            ArticleDetailSerializer(article, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Partially update an article",
        request=ArticleCreateUpdateSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def partial_update(self, request: Request, pk: str | None = None) -> Response:
        """Partially update an article. Author, editor, or admin only."""
        try:
            obj = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        IsAuthorOrEditorOrAdmin().check_object_permission_or_deny(request, obj)
        serializer = ArticleCreateUpdateSerializer(
            obj, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        article = serializer.save()
        return Response(
            ArticleDetailSerializer(article, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete an article",
        responses={
            204: OpenApiResponse(description="Deleted"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def destroy(self, request: Request, pk: str | None = None) -> Response:
        """Soft-delete an article. Author, editor, or admin only."""
        try:
            obj = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        IsAuthorOrEditorOrAdmin().check_object_permission_or_deny(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Add a comment to an article",
        request=CommentCreateSerializer,
        responses={
            201: CommentSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Article not found"),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="comments",
        permission_classes=[IsAuthenticated],
    )
    def comments(self, request: Request, pk: str | None = None) -> Response:
        """Add a comment or reply to an article."""
        try:
            Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentCreateSerializer(
            data={**request.data, "article": pk},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Add a reaction to an article",
        request=ReactionSerializer,
        responses={
            201: ReactionSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Article not found"),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="reactions",
        permission_classes=[IsAuthenticated],
    )
    def reactions(self, request: Request, pk: str | None = None) -> Response:
        """React to an article."""
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReactionSerializer(
            data={**request.data, "article": pk},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        reaction = serializer.save(user=request.user, article=article)
        return Response(
            ReactionSerializer(reaction).data, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Increment article view count",
        responses={
            200: OpenApiResponse(description="view_count incremented"),
            404: OpenApiResponse(description="Not found"),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="view",
        permission_classes=[AllowAny],
    )
    def view(self, request: Request, pk: str | None = None) -> Response:
        """Increment the view counter for an article."""
        updated = Article.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
        if not updated:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)


class CommentViewSet(ViewSet):
    """CRUD operations for comments."""

    @extend_schema(
        summary="List all comments",
        responses={
            200: CommentSerializer(many=True),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: Request) -> Response:
        """Return all active comments."""
        qs = (
            Comment.objects.filter(is_active=True)
            .select_related("user")
            .order_by("created_at")
        )
        return Response(
            CommentSerializer(qs, many=True).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Retrieve a comment",
        responses={
            200: CommentSerializer,
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """Return a single comment by primary key."""
        try:
            obj = Comment.objects.get(pk=pk, is_active=True)
        except Comment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(CommentSerializer(obj).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a comment",
        request=CommentCreateSerializer,
        responses={
            201: CommentSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def create(self, request: Request) -> Response:
        """Create a new comment. Authenticated users only."""
        IsAuthenticated().check_permission_or_deny(request)
        serializer = CommentCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Partially update a comment",
        request=CommentCreateSerializer,
        responses={
            200: CommentSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def partial_update(self, request: Request, pk: str | None = None) -> Response:
        """Partially update a comment. Author or admin only."""
        try:
            obj = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        IsCommentAuthorOrAdmin().check_object_permission_or_deny(request, obj)
        serializer = CommentCreateSerializer(
            obj, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a comment",
        responses={
            204: OpenApiResponse(description="Deleted"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def destroy(self, request: Request, pk: str | None = None) -> Response:
        """Soft-delete a comment. Author or admin only."""
        try:
            obj = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        IsCommentAuthorOrAdmin().check_object_permission_or_deny(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReactionViewSet(ViewSet):
    """CRUD operations for reactions."""

    @extend_schema(
        summary="List all reactions",
        responses={
            200: ReactionSerializer(many=True),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def list(self, request: Request) -> Response:
        """Return all reactions."""
        qs = Reaction.objects.select_related("user", "article", "comment")
        return Response(
            ReactionSerializer(qs, many=True).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Retrieve a reaction",
        responses={
            200: ReactionSerializer,
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        """Return a single reaction by primary key."""
        try:
            obj = Reaction.objects.get(pk=pk)
        except Reaction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ReactionSerializer(obj).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a reaction",
        request=ReactionSerializer,
        responses={
            201: ReactionSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Unauthorized"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def create(self, request: Request) -> Response:
        """Create a reaction. Authenticated users only."""
        IsAuthenticated().check_permission_or_deny(request)
        serializer = ReactionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        reaction = serializer.save(user=request.user)
        return Response(
            ReactionSerializer(reaction).data, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Delete a reaction",
        responses={
            204: OpenApiResponse(description="Deleted"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not found"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def destroy(self, request: Request, pk: str | None = None) -> Response:
        """Delete a reaction. Reaction owner only."""
        IsAuthenticated().check_permission_or_deny(request)
        try:
            obj = Reaction.objects.get(pk=pk)
        except Reaction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if obj.user_id != request.user.pk:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
