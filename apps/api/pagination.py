from rest_framework.pagination import PageNumberPagination


class OptionalPageNumberPagination(PageNumberPagination):
    """
    صفحه‌بندی سازگار با کلاینت‌های فعلی.

    - بدون پارامتر ``page`` یا ``page_size``: همان لیست ساده‌ی قبلی برمی‌گردد.
    - با ``?page=2`` یا ``?page_size=10``: پاسخ صفحه‌بندی‌شده
      (count / next / previous / results).

    اگر خواستید صفحه‌بندی همیشه فعال باشد، ``paginate_by_default = True``
    بگذارید (در این حالت تست‌هایی که لیست ساده انتظار دارند باید
    به ``response.data["results"]`` تغییر کنند).
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    paginate_by_default = False

    def paginate_queryset(self, queryset, request, view=None):
        wants_page = (
            self.page_query_param in request.query_params
            or self.page_size_query_param in request.query_params
        )

        if not (self.paginate_by_default or wants_page):
            return None

        if hasattr(queryset, "ordered") and not queryset.ordered:
            queryset = queryset.order_by("pk")

        return super().paginate_queryset(queryset, request, view)
