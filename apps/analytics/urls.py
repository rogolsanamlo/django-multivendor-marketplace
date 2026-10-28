from django.urls import path

from .views import (
    ExportPDFView,
    ExportSalesExcelView,
    ReportsView,
    SellerAnalyticsDashboardView,
)


app_name = "analytics"


urlpatterns = [

    path(
        "seller/dashboard/",
        SellerAnalyticsDashboardView.as_view(),
        name="seller_dashboard",
    ),

    path(
        "seller/reports/",
        ReportsView.as_view(),
        name="reports",
    ),

    path(
        "seller/reports/export-pdf/",
        ExportPDFView.as_view(),
        name="export_pdf",
    ),

    path(
        "seller/reports/export-excel/",
        ExportSalesExcelView.as_view(),
        name="export_excel",
    ),

]