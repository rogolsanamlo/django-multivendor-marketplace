from django.urls import include, path


app_name = "api"


urlpatterns = [

    path(
        "",
        include("apps.api.urls.accounts"),
    ),

    path(
        "",
        include("apps.api.urls.products"),
    ),

    path(
        "",
        include(
            "apps.api.urls.comment_scoring_favorites"
        ),
    ),

    path(
        "",
        include("apps.api.urls.orders"),
    ),

    path(
        "analytics/",
        include("apps.api.urls.analytics"),
    ),
       path(
            "payments/",
include("apps.api.urls.payments"),  ),
       path(
    "discounts/",
    include("apps.api.urls.discounts"),
),

  path(
    "",
    include("apps.api.urls.warehouses"),
),
     path(
    "",
    include("apps.api.urls.search"),
),
]


