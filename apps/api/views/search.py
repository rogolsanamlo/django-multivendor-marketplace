from django.db.models import Q

from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.products.models import StoreProduct
from apps.api.serializers.search import SearchResultSerializer


class SearchResultsAPIView(ListAPIView):

    serializer_class = SearchResultSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        query = self.request.GET.get(
            "q",
            ""
        ).strip()

        products = StoreProduct.objects.select_related(
            "product",
            "store"
        ).filter(
            is_active=True
        )

        if query:
            products = products.filter(
                Q(
                    product__product_name__icontains=query
                )
                |
                Q(
                    product__description__icontains=query
                )
            )

        return products