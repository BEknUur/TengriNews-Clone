"""Serializers for categories, tags, articles, comments, and reactions."""

from __future__ import annotations

from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

from apps.main.models import Article, Category, Comment, Reaction, Tag


class CategorySerializer(ModelSerializer):
    """Serialize a Category with optional parent nesting."""

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
    """Serialize a Tag."""

    class Meta:
        model = Tag
        fields: tuple[str, ...] = ("id", "name", "slug")


class ArticleListSerializer(ModelSerializer):
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

    def get_author(self, obj: Article) -> dict | None:
        """Return a minimal author representation."""
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

    def get_comments(self, obj: Article) -> list[dict]:
        """Return active top-level comments for the article."""
        qs = obj.comments.filter(is_active=True, parent=None).order_by("created_at")
        return CommentSerializer(qs, many=True).data

    def get_reactions_count(self, obj: Article) -> int:
        """Return the total number of reactions on the article."""
        return obj.reactions.count()


class ArticleCreateUpdateSerializer(ModelSerializer):
    """Serializer for creating and updating articles."""

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

    def create(self, validated_data: dict) -> Article:
        """Create article, set author from request context, and assign tags."""
        tags = validated_data.pop("tags", [])
        article = Article.objects.create(
            author=self.context["request"].user,
            **validated_data,
        )
        article.tags.set(tags)
        return article

    def update(self, instance: Article, validated_data: dict) -> Article:
        """Update article fields and replace tag set."""
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class CommentSerializer(ModelSerializer):
    """Serialize a comment with nested replies and user info."""

    user = SerializerMethodField()
    replies = SerializerMethodField()

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

    def get_user(self, obj: Comment) -> dict | None:
        """Return minimal user representation."""
        if obj.user is None:
            return None
        return {"id": obj.user_id, "email": obj.user.email}

    def get_replies(self, obj: Comment) -> list[dict]:
        """Return active direct replies to this comment."""
        qs = obj.replies.filter(is_active=True).order_by("created_at")
        return CommentSerializer(qs, many=True).data


class CommentCreateSerializer(ModelSerializer):
    """Serializer for creating a new comment or reply."""

    class Meta:
        model = Comment
        fields: tuple[str, ...] = ("article", "parent", "content")

    def validate(self, attrs: dict) -> dict:
        """Ensure the parent comment belongs to the same article."""
        parent = attrs.get("parent")
        if parent and parent.article_id != attrs["article"].pk:
            raise ValidationError(
                {"parent": "Parent comment must belong to the same article."}
            )
        return attrs

    def create(self, validated_data: dict) -> Comment:
        """Create the comment and attach the authenticated user."""
        return Comment.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )


class ReactionSerializer(ModelSerializer):
    """Serializer for creating and reading reactions."""

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

    def validate(self, attrs: dict) -> dict:
        """Ensure the reaction targets exactly one of article or comment."""
        has_article = bool(attrs.get("article"))
        has_comment = bool(attrs.get("comment"))
        if has_article == has_comment:
            raise ValidationError(
                "A reaction must target either an article or a comment, not both."
            )
        return attrs
