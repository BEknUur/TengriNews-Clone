from rest_framework import serializers
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings

from apps.main.models import Category, Tag, Article, Comment, Reaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent", "created_at", "updated_at")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class ArticleListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Article
        fields = (
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

    def get_author(self, obj):
        user = getattr(obj, "author", None)
        if not user:
            return None
        return {"id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name}


class ArticleDetailSerializer(ArticleListSerializer):
    content = serializers.CharField()
    comments = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + ("content", "comments", "reactions_count")

    def get_comments(self, obj):
        qs = obj.comments.filter(is_active=True).order_by("created_at")
        return CommentSerializer(qs, many=True).data

    def get_reactions_count(self, obj):
        return obj.reactions.count()


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Article
        fields = ("title", "slug", "excerpt", "content", "category", "tags", "is_published")

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        request = self.context.get("request")
        author = getattr(request, "user", None)
        validated_data["author"] = author
        with transaction.atomic():
            article = Article.objects.create(**validated_data)
            if tags:
                article.tags.set(tags)
            return article

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "article", "user", "parent", "content", "is_active", "created_at", "replies")

    def get_user(self, obj):
        user = getattr(obj, "user", None)
        if not user:
            return None
        return {"id": user.id, "email": user.email, "first_name": user.first_name}

    def get_replies(self, obj):
        qs = obj.replies.filter(is_active=True).order_by("created_at")
        return CommentSerializer(qs, many=True).data


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("article", "parent", "content")

    def validate(self, data):
        parent = data.get("parent")
        article = data.get("article")
        if parent and parent.article_id != article.id:
            raise serializers.ValidationError("Parent must belong to same article.")
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        validated_data["user"] = user
        return super().create(validated_data)


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ("id", "user", "article", "comment", "type", "created_at")
        read_only_fields = ("user",)

    def validate(self, data):
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

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)