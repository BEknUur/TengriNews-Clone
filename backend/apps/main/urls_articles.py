from django.urls import path
from apps.main.views.article_api import (
    ArticleListCreateView,
    ArticleDetailView,
    ArticleCommentsView,
    ArticleReactionsView,
    ArticleViewIncrementView,
    ArticleBookmarkView,
)

urlpatterns = [
    path("", ArticleListCreateView.as_view(), name="articles-list-create"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="articles-detail"),
    path("<int:pk>/comments/", ArticleCommentsView.as_view(), name="articles-comments"),
    path("<int:pk>/reactions/", ArticleReactionsView.as_view(), name="articles-reactions"),
    path("<int:pk>/react/", ArticleReactionsView.as_view(), name="articles-react-compat"),
    path("<int:pk>/view/", ArticleViewIncrementView.as_view(), name="articles-view"),
    path("<int:pk>/bookmark/", ArticleBookmarkView.as_view(), name="articles-bookmark"),
]
