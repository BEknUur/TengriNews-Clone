"""Models for the main news domain: Category, Tag, Article, Comment, Reaction."""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    Index,
    ManyToManyField,
    PositiveIntegerField,
    SlugField,
    TextField,
    TextChoices,
    UniqueConstraint,
    JSONField,
    Q,
    CASCADE,
    SET_NULL,
)
from django.utils import timezone

from apps.abstracts.models import AbstractTimeStamptModel

# Constants
CATEGORY_NAME_MAX_LENGTH: int = 255
CATEGORY_SLUG_MAX_LENGTH: int = 255
TAG_NAME_MAX_LENGTH: int = 255
TAG_SLUG_MAX_LENGTH: int = 255
ARTICLE_TITLE_MAX_LENGTH: int = 255
ARTICLE_SLUG_MAX_LENGTH: int = 255
REACTION_TYPE_MAX_LENGTH: int = 10


class Category(AbstractTimeStamptModel):
    """Hierarchical article category."""

    name = CharField(max_length=CATEGORY_NAME_MAX_LENGTH, unique=True)
    slug = SlugField(max_length=CATEGORY_SLUG_MAX_LENGTH, unique=True)
    parent = ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="children",
    )

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Category(id={self.pk}, name={self.name!r})"


class Tag(AbstractTimeStamptModel):
    """Article tag for grouping and filtering."""

    name = CharField(max_length=TAG_NAME_MAX_LENGTH, unique=True)
    slug = SlugField(max_length=TAG_SLUG_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Tag(id={self.pk}, name={self.name!r})"


class Article(AbstractTimeStamptModel):
    """News article written by an author and belonging to a category."""

    title = CharField(max_length=ARTICLE_TITLE_MAX_LENGTH)
    slug = SlugField(max_length=ARTICLE_SLUG_MAX_LENGTH, unique=True)
    excerpt = TextField(blank=True)
    content = TextField()
    author = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name="articles",
    )
    category = ForeignKey(
        Category,
        on_delete=SET_NULL,
        null=True,
        related_name="articles",
    )
    tags = ManyToManyField(Tag, blank=True, related_name="articles")
    is_published = BooleanField(default=False, db_index=True)
    published_at = DateTimeField(null=True, blank=True)
    view_count = PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_at", "-id"]
        indexes = [
            Index(fields=["published_at", "id"]),
        ]

    def save(self, *args, **kwargs) -> None:
        """Auto-set published_at when article is first published."""
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f"Article(id={self.pk}, title={self.title!r})"


class Comment(AbstractTimeStamptModel):
    """User comment on an article, with optional parent for nested replies."""

    article = ForeignKey(
        Article,
        on_delete=CASCADE,
        related_name="comments",
    )
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="comments",
    )
    parent = ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=CASCADE,
        related_name="replies",
    )
    content = TextField()
    is_active = BooleanField(default=True)

    class Meta:
        ordering = ["created_at"]

    def clean(self) -> None:
        """Validate that a reply belongs to the same article as its parent."""
        if self.parent and self.parent.article_id != self.article_id:
            raise ValidationError("Parent comment must belong to the same article.")

    def __str__(self) -> str:
        return f"Comment #{self.pk} by {self.user}"

    def __repr__(self) -> str:
        return f"Comment(id={self.pk}, user={self.user})"


class Reaction(AbstractTimeStamptModel):
    """A user reaction (like, dislike, etc.) on an article or comment."""

    class ReactionType(TextChoices):
        LIKE = "like", "Like"
        DISLIKE = "dislike", "Dislike"
        LOVE = "love", "Love"
        LAUGH = "laugh", "Laugh"

    # Convenience constants for tests and external code
    LIKE = ReactionType.LIKE
    DISLIKE = ReactionType.DISLIKE
    LOVE = ReactionType.LOVE
    LAUGH = ReactionType.LAUGH

    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name="reactions",
    )
    article = ForeignKey(
        Article,
        null=True,
        blank=True,
        on_delete=CASCADE,
        related_name="reactions",
    )
    comment = ForeignKey(
        Comment,
        null=True,
        blank=True,
        on_delete=CASCADE,
        related_name="reactions",
    )
    type = CharField(max_length=REACTION_TYPE_MAX_LENGTH, choices=ReactionType.choices)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "article"],
                condition=Q(article__isnull=False),
                name="unique_user_article_reaction",
            ),
            UniqueConstraint(
                fields=["user", "comment"],
                condition=Q(comment__isnull=False),
                name="unique_user_comment_reaction",
            ),
        ]

    def clean(self) -> None:
        """Validate that reaction targets exactly one of article or comment."""
        if bool(self.article_id) == bool(self.comment_id):
            raise ValidationError(
                "Reaction must be attached to exactly one of article or comment."
            )

    def __str__(self) -> str:
        target = self.article or self.comment
        return f"Reaction {self.type} by {self.user} on {target}"

    def __repr__(self) -> str:
        return f"Reaction(id={self.pk}, type={self.type!r}, user={self.user})"


class Bookmark(AbstractTimeStamptModel):
    """Saved article for a user."""

    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name="bookmarks",
    )
    article = ForeignKey(
        Article,
        on_delete=CASCADE,
        related_name="bookmarks",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(
                fields=["user", "article"],
                condition=Q(deleted_at__isnull=True),
                name="unique_active_user_article_bookmark",
            ),
        ]

    def __str__(self) -> str:
        return f"Bookmark user={self.user_id} article={self.article_id}"

    def __repr__(self) -> str:
        return f"Bookmark(id={self.pk}, user={self.user_id}, article={self.article_id})"


class ArticleAuditLog(AbstractTimeStamptModel):
    """Audit record for article create/update events."""

    class Action(TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"

    article = ForeignKey(
        Article,
        on_delete=CASCADE,
        related_name="audit_logs",
    )
    actor = ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="article_audit_logs",
    )

    action = CharField(max_length=20, choices=Action.choices)
    snapshot = JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["article", "-created_at"]),
            Index(fields=["actor", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"ArticleAuditLog article={self.article_id} action={self.action}"
