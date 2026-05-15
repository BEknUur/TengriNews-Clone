# Django modules
from django.contrib import admin
from django.urls import include, path
from apps.main.views.async_endpoint import ExternalDataView

# Third-party modules
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

# Project modules
from apps.main.views import (
    ArticleViewSet,
    BookmarkViewSet,
    CategoryViewSet,
    CommentViewSet,
    ReactionViewSet,
    TagViewSet,
)

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
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/external/", ExternalDataView.as_view(), name="external-data"),
]
