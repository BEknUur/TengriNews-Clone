from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.main.models import Category, Tag, Article, Comment, Reaction
from apps.main.serializers import (
    CategorySerializer, TagSerializer,
    ArticleListSerializer, ArticleDetailSerializer, ArticleCreateUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, ReactionSerializer
)
from apps.main.permissions import IsAdminOnly, IsAuthorOrEditorOrAdmin, IsCommentAuthorOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminOnly()]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminOnly()]

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().select_related("author", "category").prefetch_related("tags")
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("category", "tags", "author", "is_published")
    search_fields = ("title", "content")
    ordering_fields = ("published_at", "view_count")
    pagination_class = None  # or your pagination class

    def get_serializer_class(self):
        if self.action == "list":
            return ArticleListSerializer
        if self.action == "retrieve":
            return ArticleDetailSerializer
        return ArticleCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthorOrEditorOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        article = self.get_object()
        data = request.data.copy()
        data["article"] = article.id
        serializer = CommentCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reactions(self, request, pk=None):
        article = self.get_object()
        data = request.data.copy()
        data["article"] = article.id
        serializer = ReactionSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        reaction = serializer.save()
        return Response(ReactionSerializer(reaction).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def view(self, request, pk=None):
        article = self.get_object()
        article.view_count = (article.view_count or 0) + 1
        article.save(update_fields=["view_count"])
        return Response({"view_count": article.view_count}, status=status.HTTP_200_OK)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related("user", "article")
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsCommentAuthorOrAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return CommentCreateSerializer
        return CommentSerializer

class ReactionViewSet(viewsets.ModelViewSet):
    queryset = Reaction.objects.all().select_related("user", "article", "comment")
    serializer_class = ReactionSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]