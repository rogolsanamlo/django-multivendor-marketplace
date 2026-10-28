from django.db.models import Q
from django.shortcuts import render
from django.views import View

from apps.products.models import StoreProduct


class SearchResultsView(View):

    def get(self, request, *args, **kwargs):
        query = request.GET.get(
            "q",
            "",
        ).strip()

        products = (
            StoreProduct.objects
            .select_related(
                "product",
                "store",
            )
            .filter(
                is_active=True,
            )
        )

        if query:
            products = products.filter(
                Q(
                    product__product_name__icontains=query
                )
                | Q(
                    product__description__icontains=query
                )
            )

        context = {
            "products": products,
        }

        return render(
            request,
            "search_app/search_results.html",
            context,
        )


