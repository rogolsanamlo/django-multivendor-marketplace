from django.urls import path

from apps.api.views.search import SearchResultsAPIView


urlpatterns = [
    path(
        "search/",
        SearchResultsAPIView.as_view(),
        name="search",
    ),
]