from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Tag, Article, Comment, Reaction

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Reaction)