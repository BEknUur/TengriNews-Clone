from django.contrib import admin

# Register your models here.
from .models import Article, ArticleAuditLog, Bookmark, Category, Comment, Reaction, Tag

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(Bookmark)
admin.site.register(ArticleAuditLog)
