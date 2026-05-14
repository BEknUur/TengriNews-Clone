from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.main.views import (
    ArticleViewSet,
    BookmarkViewSet,
    CategoryViewSet,
    CommentViewSet,
    ReactionViewSet,
    TagViewSet,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"articles", ArticleViewSet, basename="articles")
router.register(r"comments", CommentViewSet, basename="comments")
router.register(r"reactions", ReactionViewSet, basename="reactions")
router.register(r"bookmarks", BookmarkViewSet, basename="bookmarks")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/accounts/", include("apps.accounts.auth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
