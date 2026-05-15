from __future__ import annotations

from django.db.models import F, Prefetch
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from apps.core.pagination_selector import get_paginator
from apps.main.models import Article, Bookmark, Comment
from apps.main.serializers import (
    ArticleCreateUpdateSerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    BookmarkSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    ReactionSerializer,
)
from apps.main.permissions import IsAuthorOrEditorOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging

logger = logging.getLogger(__name__)


class ArticleListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request):
        qs = (
            Article.objects.filter(deleted_at__isnull=True)
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-published_at", "-id")
        )
        paginator = get_paginator(request, self)
        page = paginator.paginate_queryset(qs, request)
        serializer = ArticleListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=HTTP_401_UNAUTHORIZED)
        
        serializer = ArticleCreateUpdateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        article = serializer.save()
        logger.info("Article created: id=%s by user_id=%s", article.pk, getattr(request.user, "pk", None))
        out = ArticleDetailSerializer(article, context={"request": request})
        return Response(out.data, status=HTTP_201_CREATED)


class ArticleDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(
            Article.objects.filter(deleted_at__isnull=True)
            .select_related("author", "category")
            .prefetch_related(
                "tags",
                Prefetch(
                    "comments",
                    queryset=Comment.objects.filter(is_active=True, parent=None)
                    .select_related("user")
                    .prefetch_related(
                        Prefetch(
                            "replies",
                            queryset=Comment.objects.filter(is_active=True).select_related("user"),
                        )
                    ),
                ),
                "reactions",
            ),
            pk=pk,
        )

    def get(self, request: Request, pk: int):
        article = self.get_object(pk)
        serializer = ArticleDetailSerializer(article, context={"request": request})
        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request: Request, pk: int):
        article = self.get_object(pk)
        IsAuthorOrEditorOrAdmin().check_object_permission_or_deny(request, article)
        serializer = ArticleCreateUpdateSerializer(instance=article, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        article = serializer.save()
        out = ArticleDetailSerializer(article, context={"request": request})
        return Response(out.data, status=HTTP_200_OK)

    def delete(self, request: Request, pk: int):
        article = self.get_object(pk)
        IsAuthorOrEditorOrAdmin().check_object_permission_or_deny(request, article)
        article.delete()
        logger.info("Article soft-deleted: id=%s by user_id=%s", pk, getattr(request.user, "pk", None))
        return Response(status=HTTP_204_NO_CONTENT)


class ArticleCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: int):
        article = get_object_or_404(Article.objects.filter(deleted_at__isnull=True), pk=pk)
        data = dict(request.data)
        data["article"] = article.pk
        serializer = CommentCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        out = CommentSerializer(comment)
        return Response(out.data, status=HTTP_201_CREATED)


class ArticleReactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: int):
        article = get_object_or_404(Article.objects.filter(deleted_at__isnull=True), pk=pk)
        raw_type = request.data.get("type")
        if isinstance(raw_type, (list, tuple)):
            raw_type = raw_type[0] if raw_type else None
        data = {"type": raw_type, "article": article.pk}
        serializer = ReactionSerializer(data=data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            try:
                detail = exc.detail
            except Exception:
                detail = str(exc)
            logger.warning(
                "Reaction validation failed user=%s article=%s errors=%s data=%s",
                getattr(request, "user", None),
                getattr(article, "pk", None),
                detail,
                dict(request.data),
            )
            return Response({"detail": "validation_error", "errors": detail, "request_data": dict(request.data)}, status=HTTP_400_BAD_REQUEST)
        reaction = serializer.save(user=request.user, article=article)
        out = ReactionSerializer(reaction)
        return Response(out.data, status=HTTP_201_CREATED)


class ArticleViewIncrementView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, pk: int):
        updated = Article.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
        if not updated:
            return Response({"detail": "Not found."}, status=HTTP_404_NOT_FOUND)
        return Response({"detail": "ok"}, status=HTTP_200_OK)


class ArticleBookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, pk: int):
        article = get_object_or_404(Article.objects.filter(deleted_at__isnull=True), pk=pk)
        bookmark = Bookmark.objects.filter(user=request.user, article=article, deleted_at__isnull=True).first()
        if bookmark:
            bookmark.delete()
        return Response({"detail": "Bookmark removed."}, status=HTTP_200_OK)

    def post(self, request: Request, pk: int):
        article = get_object_or_404(Article.objects.filter(deleted_at__isnull=True), pk=pk)
        bookmark = Bookmark.objects.filter(user=request.user, article=article).first()
        if bookmark and bookmark.deleted_at is not None:
            bookmark.deleted_at = None
            bookmark.save(update_fields=["deleted_at", "updated_at"])
            out = BookmarkSerializer(bookmark)
            return Response(out.data, status=HTTP_201_CREATED)
        if bookmark:
            out = BookmarkSerializer(bookmark)
            return Response(out.data, status=HTTP_200_OK)
        bookmark = Bookmark.objects.create(user=request.user, article=article)
        out = BookmarkSerializer(bookmark)
        return Response(out.data, status=HTTP_201_CREATED)
