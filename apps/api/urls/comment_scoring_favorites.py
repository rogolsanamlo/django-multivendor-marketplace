from django.urls import path

from apps.api.views.comment_scoring_favorites import (
    CommentListAPIView,
    CommentDetailAPIView,

    ScoringListAPIView,
    ScoringDetailAPIView,

    FavoriteListAPIView,
    FavoriteDetailAPIView,
)



urlpatterns = [
  
    path(
    "comments/",
    CommentListAPIView.as_view(),
    name="comment-list"
),

path(
    "comments/<int:pk>/",
    CommentDetailAPIView.as_view(),
    name="comment-detail"
),

path(
    "scores/",
    ScoringListAPIView.as_view(),
    name="scoring-list"
),

path(
    "scores/<int:pk>/",
    ScoringDetailAPIView.as_view(),
    name="scoring-detail"
),

path(
    "favorites/",
    FavoriteListAPIView.as_view(),
    name="favorite-list"
),

path(
    "favorites/<int:pk>/",
    FavoriteDetailAPIView.as_view(),
    name="favorite-detail"
),

]




