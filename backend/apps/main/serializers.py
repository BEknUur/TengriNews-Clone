"""Serializers for categories, tags, articles, comments, and reactions."""

from __future__ import annotations

from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

# Project modules
from apps.main.models import Category, Tag, Article, Comment, Reaction


class CategorySerializer(ModelSerializer):
    """Serialize a Category with optional parent nesting."""

    """Serializer for category read/write payloads."""

    class Meta:
        model = Category
        fields: tuple[str, ...] = (
            "id",
            "name",
            "slug",
            "parent",
            "created_at",
            "updated_at",
        )


class TagSerializer(ModelSerializer):
    """Serializer for tag read/write payloads."""

    """Serialize a Tag."""

    class Meta:
        model = Tag
        fields: tuple[str, ...] = ("id", "name", "slug")


class ArticleListSerializer(ModelSerializer):
    """Serializer for article list responses."""

    """Lightweight article serializer used in list views."""

    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    author = SerializerMethodField()

    class Meta:
        model = Article
        fields: tuple[str, ...] = (
            "id",
            "title",
            "slug",
            "excerpt",
            "author",
            "category",
            "tags",
            "is_published",
            "published_at",
            "view_count",
            "created_at",
        )

    def get_author(self, obj: Article) -> dict[str, Any] | None:
        """Return compact author representation for list/detail views."""
        user = getattr(obj, "author", None)
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }


class ArticleDetailSerializer(ArticleListSerializer):
    """Serializer for article detail responses."""

    """Full article serializer including content, comments, and reaction counts."""

    content = CharField()
    comments = SerializerMethodField()
    reactions_count = SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + (
            "content",
            "comments",
            "reactions_count",
        )

    def get_comments(self, obj: Article) -> list[dict[str, Any]]:
        """Return active comments ordered by creation time."""
        qs = obj.comments.filter(is_active=True).order_by("created_at")
        return CommentSerializer(qs, many=True).data

    def get_reactions_count(self, obj: Article) -> int:
        """Return reactions count for the article."""
        return obj.reactions.count()


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for article create/update requests."""

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Article
        fields: tuple[str, ...] = (
            "title",
            "slug",
            "excerpt",
            "content",
            "category",
            "tags",
            "is_published",
        )

    def create(self, validated_data: dict[str, Any]) -> Article:
        """Create article in transaction and set related tags."""
        tags = validated_data.pop("tags", [])
        article = Article.objects.create(
            author=self.context["request"].user,
            **validated_data,
        )
        article.tags.set(tags)
        return article

    def update(self, instance: Article, validated_data: dict[str, Any]) -> Article:
        """Update article fields and replace tags when provided."""
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comment read responses with nested user/replies."""

    user = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields: tuple[str, ...] = (
            "id",
            "article",
            "user",
            "parent",
            "content",
            "is_active",
            "created_at",
            "replies",
        )

    def get_user(self, obj: Comment) -> dict[str, Any] | None:
        """Return compact comment author representation."""
        user = getattr(obj, "user", None)
        if not user:
            return None
        return {"id": obj.user_id, "email": obj.user.email}

    def get_replies(self, obj: Comment) -> list[dict[str, Any]]:
        """Return active nested replies."""
        qs = obj.replies.filter(is_active=True).order_by("created_at")
        return CommentSerializer(qs, many=True).data


class CommentCreateSerializer(ModelSerializer):
    """Serializer for comment creation payload."""

    """Serializer for creating a new comment or reply."""

    class Meta:
        model = Comment
        fields: tuple[str, ...] = ("article", "parent", "content")

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate that parent comment belongs to same article."""
        parent = data.get("parent")
        article = data.get("article")
        if parent and parent.article_id != article.id:
            raise serializers.ValidationError("Parent must belong to same article.")
        return data

    def create(self, validated_data: dict[str, Any]) -> Comment:
        """Create comment and bind current authenticated user."""
        request = self.context.get("request")
        user = getattr(request, "user", None)
        validated_data["user"] = user
        return super().create(validated_data)


class ReactionSerializer(ModelSerializer):
    """Serializer for creating and reading reactions."""

    """Serializer for reaction create/read payloads."""

    class Meta:
        model = Reaction
        fields: tuple[str, ...] = (
            "id",
            "user",
            "article",
            "comment",
            "type",
            "created_at",
        )
        read_only_fields = ("user",)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate reaction target and uniqueness constraints per user."""
        # exactly one target must be provided
        has_article = bool(data.get("article"))
        has_comment = bool(data.get("comment"))
        if has_article == has_comment:
            raise serializers.ValidationError("Provide exactly one target: article or comment.")

        user = self.context["request"].user
        if has_article:
            if Reaction.objects.filter(user=user, article=data["article"]).exists():
                raise serializers.ValidationError("You already reacted to this article.")
        if has_comment:
            if Reaction.objects.filter(user=user, comment=data["comment"]).exists():
                raise serializers.ValidationError("You already reacted to this comment.")
        return data

    def create(self, validated_data: dict[str, Any]) -> Reaction:
        """Create reaction for current authenticated user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
