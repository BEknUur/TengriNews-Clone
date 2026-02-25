from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


from apps.abstract.models import AbstractTimeStamptModel

class Category(AbstractTimeStamptModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
class Tag(AbstractTimeStamptModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
class Article(AbstractTimeStamptModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="articles"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    is_published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["-published_at"])]

    def save(self, *args, **kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Comment(AbstractTimeStamptModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created_at"]
    
    def clean(self):
        if self.parent and self.parent.article != self.article:
            raise ValidationError("Parent comment must belong to the same article.")
        
    def __str__(self):
        return f"Comment by {self.pk} on {self.user}"
    

class Reaction(AbstractTimeStamptModel):
    LIKE = "like"
    DISLIKE = "dislike"
    LOVE = "love"
    LAUGH = "laugh"

    REACTION_CHOICES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
        (LOVE, "Love"),
        (LAUGH, "Laugh"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reactions")
    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.CASCADE, related_name="reactions")
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name="reactions")
    type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "article"], name="unique_user_article_reaction", condition=models.Q(article__isnull=False)),
            models.UniqueConstraint(fields=["user", "comment"], name="unique_user_comment_reaction", condition=models.Q(comment__isnull=False)),
        ]

    def clean(self):
        # exactly one target must be set (article xor comment)
        if bool(self.article) == bool(self.comment):
            raise ValidationError("Reaction must be attached to exactly one of article or comment")

    def __str__(self):
        target = self.article or self.comment
        return f"Reaction {self.type} by {self.user} on {target}"