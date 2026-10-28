from django.urls import path

from apps.api.views.accounts import (
    UserProfileAPIView,
    UpdateProfileAPIView,
    MyStoreAPIView,
    CreateStoreAPIView,
    UpdateStoreAPIView,
)


urlpatterns = [

    path(
        "profile/",
        UserProfileAPIView.as_view(),
        name="profile"
    ),

    path(
        "profile/update/",
        UpdateProfileAPIView.as_view(),
        name="profile-update"
    ),

    path(
        "store/",
        MyStoreAPIView.as_view(),
        name="my-store"
    ),

    path(
        "store/create/",
        CreateStoreAPIView.as_view(),
        name="store-create"
    ),

    path(
        "store/update/",
        UpdateStoreAPIView.as_view(),
        name="store-update"
    ),

]