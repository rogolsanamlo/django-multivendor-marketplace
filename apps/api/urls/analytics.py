from django.urls import path

from apps.api.views.analytics import (
    AnalyticsDashboardAPIView,
    TopProductsAPIView,
    TopCategoriesAPIView,
    DailySalesAPIView,
    ProductsWithoutSalesAPIView,
    MonthlyIncomeAPIView,
    LowStockProductsAPIView,
    LastOrdersAPIView,
    TopCustomersAPIView,
    LastSevenDaysSalesAPIView,
)


urlpatterns = [

    path(
        "<int:store_id>/dashboard/",
        AnalyticsDashboardAPIView.as_view(),
        name="dashboard",
    ),

    path(
        "<int:store_id>/top-products/",
        TopProductsAPIView.as_view(),
        name="top-products",
    ),

    path(
        "<int:store_id>/top-categories/",
        TopCategoriesAPIView.as_view(),
        name="top-categories",
    ),

    path(
        "<int:store_id>/daily-sales/",
        DailySalesAPIView.as_view(),
        name="daily-sales",
    ),

    path(
        "<int:store_id>/products-without-sales/",
        ProductsWithoutSalesAPIView.as_view(),
        name="products-without-sales",
    ),

    path(
        "<int:store_id>/monthly-income/",
        MonthlyIncomeAPIView.as_view(),
        name="monthly-income",
    ),

    path(
        "<int:store_id>/low-stock-products/",
        LowStockProductsAPIView.as_view(),
        name="low-stock-products",
    ),

    path(
        "<int:store_id>/last-orders/",
        LastOrdersAPIView.as_view(),
        name="last-orders",
    ),

    path(
        "<int:store_id>/top-customers/",
        TopCustomersAPIView.as_view(),
        name="top-customers",
    ),

    path(
        "<int:store_id>/last-seven-days-sales/",
        LastSevenDaysSalesAPIView.as_view(),
        name="last-seven-days-sales",
    ),
]