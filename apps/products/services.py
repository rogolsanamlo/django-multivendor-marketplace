from django.core.paginator import Paginator
from django.db.models import Max, Min
from django.http import QueryDict
from django.shortcuts import get_object_or_404

from apps.comment_scoring_favorites.models import Favorite, Scoring

from .filters import ProductFilter
from .models import ProductGroup, StoreProduct


def get_user_score(store_product, user):
    """The user's score (1-5) for the product, or 0 when the user has not scored it."""
    try:
        score = Scoring.objects.get(
            store_product=store_product,
            scoring_user=user
        )
        return score.score
    except Scoring.DoesNotExist:
        return 0


def get_user_favorite(store_product, user):
    return Favorite.objects.filter(
        store_product=store_product,
        favorite_user=user
    ).exists()


def get_group_and_descendant_ids(group):
    """The group's id plus the ids of all its active sub-groups."""
    seen = {group.id}
    frontier = [group.id]

    while frontier:
        frontier = [
            group_id
            for group_id in ProductGroup.objects.filter(
                is_active=True,
                group_parent_id__in=frontier
            ).values_list('id', flat=True)
            if group_id not in seen
        ]
        seen.update(frontier)

    return seen


def get_products_by_group(slug):
    current_group = get_object_or_404(
        ProductGroup,
        slug=slug
    )

    # A main group shows the products of its sub-groups too.
    products = StoreProduct.objects.filter(
        is_active=True,
        store__is_active=True,
        product__product_group__in=get_group_and_descendant_ids(
            current_group
        )
    ).distinct()

    return current_group, products


def get_price_range(products):
    return products.aggregate(
        min=Min('price'),
        max=Max('price')
    )


def build_show_count_product(
    product_count,
    per_page
):
    result = []

    i = per_page

    while i < product_count:
        result.append(i)
        i *= 2

    result.append(i)

    return result


def apply_product_filter(
    get_params: QueryDict,
    products
):
    product_filter = ProductFilter(
        get_params,
        queryset=products
    )

    return product_filter.qs, product_filter


def apply_store_filter(store_ids, products):
    if store_ids:
        products = products.filter(
            store_id__in=store_ids
        )

    return products


def paginate_products(
    page_number,
    per_page,
    products
):
    if hasattr(products, 'ordered') and not products.ordered:
        products = products.order_by('id')

    paginator = Paginator(
        products,
        per_page
    )

    return paginator.get_page(
        page_number
    )


def apply_sorting(sort_type, products):
    if sort_type == '1':
        products = products.order_by('price', 'id')
    elif sort_type == '2':
        products = products.order_by('-price', 'id')

    return products


def apply_feature_filter(feature_ids, products):
    if feature_ids:
        products = products.filter(
            product__product_feature__filter_value__id__in=feature_ids
        ).distinct()

    return products


def apply_brand_filter(brand_ids, products):
    if brand_ids:
        products = products.filter(
            product__brand__id__in=brand_ids
        )

    return products