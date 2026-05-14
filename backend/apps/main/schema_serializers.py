"""Schema serializers for OpenAPI documentation of the main app."""

# Third-party modules
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

# Project modules
from apps.main.models import Reaction


# ---------------------------------------------------------------------------
# Common
# ---------------------------------------------------------------------------


class IdErrorSerializer(serializers.Serializer):
    """Schema for object-id based error responses."""

    id = serializers.ListField(child=serializers.CharField())


class DetailErrorSerializer(serializers.Serializer):
    """Schema for detail-message error responses."""

    detail = serializers.CharField()


class EmptyResponseSerializer(serializers.Serializer):
    """Schema placeholder for empty responses."""

    pass


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------


class CategoryResponseSerializer(serializers.Serializer):
    """Schema for category response payload."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    slug = serializers.CharField()
    parent = serializers.IntegerField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CategoryCreateRequestSerializer(serializers.Serializer):
    """Schema for category create request payload."""

    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=255)
    parent = serializers.IntegerField(required=False, allow_null=True)


class CategoryPatchRequestSerializer(serializers.Serializer):
    """Schema for category partial update request payload."""

    name = serializers.CharField(max_length=255, required=False)
    slug = serializers.SlugField(max_length=255, required=False)
    parent = serializers.IntegerField(required=False, allow_null=True)


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


class TagResponseSerializer(serializers.Serializer):
    """Schema for tag response payload."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    slug = serializers.CharField()


class TagCreateRequestSerializer(serializers.Serializer):
    """Schema for tag create request payload."""

    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=255)


class TagPatchRequestSerializer(serializers.Serializer):
    """Schema for tag partial update request payload."""

    name = serializers.CharField(max_length=255, required=False)
    slug = serializers.SlugField(max_length=255, required=False)


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------


class ArticleAuthorSerializer(serializers.Serializer):
    """Schema for compact article author payload."""

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)


class ArticleCategorySerializer(serializers.Serializer):
    """Schema for nested category payload in article responses."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    parent = serializers.IntegerField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ArticleTagSerializer(serializers.Serializer):
    """Schema for nested tag payload in article responses."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)


class ArticleListItemSerializer(serializers.Serializer):
    """Schema for single article item in list responses."""

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    excerpt = serializers.CharField(read_only=True)
    author = ArticleAuthorSerializer(read_only=True)
    category = ArticleCategorySerializer(read_only=True)
    tags = ArticleTagSerializer(many=True, read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    published_at = serializers.DateTimeField(read_only=True, allow_null=True)
    view_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class ArticleDetailItemSerializer(ArticleListItemSerializer):
    """Schema for article detail response item."""

    content = serializers.CharField(read_only=True)
    comments = serializers.ListField(child=serializers.DictField(), read_only=True)
    reactions_count = serializers.IntegerField(read_only=True)


class ArticleListPaginationSerializer(serializers.Serializer):
    """Schema for pagination block in article list responses."""

    next = serializers.URLField(allow_null=True, required=False)
    previous = serializers.URLField(allow_null=True, required=False)
    next_cursor = serializers.CharField(allow_null=True, required=False)
    previous_cursor = serializers.CharField(allow_null=True, required=False)
    page_size = serializers.IntegerField(required=False)
    returned = serializers.IntegerField(required=False)
    max_page_size = serializers.IntegerField(required=False)
    ordering = serializers.CharField(required=False)
    count = serializers.IntegerField(required=False)


class ArticleListResponseSerializer(serializers.Serializer):
    """Schema for paginated article list response."""

    pagination = ArticleListPaginationSerializer(read_only=True)
    data = ArticleListItemSerializer(many=True, read_only=True)


class ArticleCreateRequestSerializer(serializers.Serializer):
    """Schema for article create request payload."""

    title = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=255)
    excerpt = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField()
    category = serializers.IntegerField(allow_null=True, required=False)
    tags = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    is_published = serializers.BooleanField(required=False)


class ArticlePatchRequestSerializer(serializers.Serializer):
    """Schema for article partial update request payload."""

    title = serializers.CharField(max_length=255, required=False)
    slug = serializers.SlugField(max_length=255, required=False)
    excerpt = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False)
    category = serializers.IntegerField(allow_null=True, required=False)
    tags = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    is_published = serializers.BooleanField(required=False)


class ArticleWriteResponseSerializer(serializers.Serializer):
    """Schema for article create/update response payload."""

    title = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    excerpt = serializers.CharField(read_only=True)
    content = serializers.CharField(read_only=True)
    category = serializers.IntegerField(read_only=True, allow_null=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(), read_only=True, allow_empty=True
    )
    is_published = serializers.BooleanField(read_only=True)


class ArticleViewCountResponseSerializer(serializers.Serializer):
    """Schema for article view increment response payload."""

    view_count = serializers.IntegerField(read_only=True)


class ArticleCommentCreateRequestSerializer(serializers.Serializer):
    """Schema for creating comment under article detail endpoint."""

    parent = serializers.IntegerField(required=False, allow_null=True)
    content = serializers.CharField()


class ArticleReactionCreateRequestSerializer(serializers.Serializer):
    """Schema for creating reaction under article detail endpoint."""

    type = serializers.ChoiceField(choices=Reaction.ReactionType.choices)


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------


class CommentUserSerializer(serializers.Serializer):
    """Schema for compact comment author payload."""

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)


class CommentResponseSerializer(serializers.Serializer):
    """Schema for comment response payload."""

    id = serializers.IntegerField(read_only=True)
    article = serializers.IntegerField(read_only=True)
    user = CommentUserSerializer(read_only=True, allow_null=True)
    parent = serializers.IntegerField(read_only=True, allow_null=True)
    content = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    replies = serializers.ListField(child=serializers.DictField(), read_only=True)


@extend_schema_serializer(component_name="CommentCreateBody")
class CommentCreateRequestSerializer(serializers.Serializer):
    """Schema for comment create request payload."""

    article = serializers.IntegerField()
    parent = serializers.IntegerField(required=False, allow_null=True)
    content = serializers.CharField()


class CommentPatchRequestSerializer(serializers.Serializer):
    """Schema for comment partial update request payload."""

    content = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)


# ---------------------------------------------------------------------------
# Reaction
# ---------------------------------------------------------------------------


class ReactionResponseSerializer(serializers.Serializer):
    """Schema for reaction response payload."""

    id = serializers.IntegerField(read_only=True)
    user = serializers.IntegerField(read_only=True)
    article = serializers.IntegerField(read_only=True, allow_null=True)
    comment = serializers.IntegerField(read_only=True, allow_null=True)
    type = serializers.ChoiceField(choices=Reaction.ReactionType.choices, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class ReactionCreateRequestSerializer(serializers.Serializer):
    """Schema for reaction create request payload."""

    article = serializers.IntegerField(required=False, allow_null=True)
    comment = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.ChoiceField(choices=Reaction.ReactionType.choices)
