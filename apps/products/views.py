from django.db.models import Count, Exists, OuterRef, Q, Value
from django.db.models.fields import BooleanField
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.accounts.models import Store
from apps.comment_scoring_favorites.models import Favorite
from apps.products.models import (
    Brand,
    FeatureValue,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.comment_scoring_favorites.forms import CommentForm
from apps.discounts.services import get_price_by_discount

from .compare import CompareStoreProduct
from .services import (
    apply_brand_filter,
    apply_feature_filter,
    apply_product_filter,
    apply_sorting,
    apply_store_filter,
    build_show_count_product,
    get_group_and_descendant_ids,
    get_price_range,
    get_products_by_group,
    get_user_score,
    paginate_products,
)


def get_root_group():
    return ProductGroup.objects.filter(
        is_active=True,
        group_parent__isnull=True
    )


def build_group_sections(request, order_by, limit=3):
    """For each root group, its own top ``limit`` products.

    Used by the tabs of the home page ("newest" / "cheapest"): the
    "all" tab shows the global list, every other tab shows only the
    products that belong to that group or to one of its sub-groups.
    """
    sections = []

    for group in get_root_group():
        products = (
            StoreProduct.objects
            .select_related('product', 'store')
            .prefetch_related('discounts__discount_basket')
            .filter(
                is_active=True,
                product__product_group__in=get_group_and_descendant_ids(
                    group
                )
            )
            .distinct()
            .order_by(order_by)
        )

        if request.user.is_authenticated:
            products = products.annotate(
                is_favorite=Exists(
                    Favorite.objects.filter(
                        store_product=OuterRef('pk'),
                        favorite_user=request.user
                    )
                )
            )
        else:
            products = products.annotate(
                is_favorite=Value(
                    False,
                    output_field=BooleanField()
                )
            )

        products = list(products[:limit])

        for item in products:
            item.final_price = get_price_by_discount(item)

        sections.append({'group': group, 'products': products})

    return sections


def get_cheapest_products(request):
    products = (
        StoreProduct.objects
        .select_related(
            'product',
            'store'
        )
        .prefetch_related(
            'discounts__discount_basket'
        )
        .filter(
            is_active=True
        )
        .order_by(
            'price'
        )[:3]
    )

    if request.user.is_authenticated:
        products = products.annotate(
            is_favorite=Exists(
                Favorite.objects.filter(
                    store_product=OuterRef('pk'),
                    favorite_user=request.user
                )
            )
        )
    else:
        products = products.annotate(
            is_favorite=Value(
                False,
                output_field=BooleanField()
            )
        )

    for item in products:
        item.final_price = get_price_by_discount(item)

    context = {
        'products': products,
        'product_groups': get_root_group(),
        'group_sections': build_group_sections(request, 'price')
    }

    return render(
        request,
        'product_app/partials/cheapest_products.html',
        context
    )


def get_last_products(request):
    products = (
        StoreProduct.objects
        .select_related(
            'product',
            'store'
        )
        .prefetch_related(
            'discounts__discount_basket'
        )
        .filter(
            is_active=True
        )
        .order_by(
            '-register_date'
        )[:3]
    )

    if request.user.is_authenticated:
        products = products.annotate(
            is_favorite=Exists(
                Favorite.objects.filter(
                    store_product=OuterRef('pk'),
                    favorite_user=request.user
                )
            )
        )
    else:
        products = products.annotate(
            is_favorite=Value(
                False,
                output_field=BooleanField()
            )
        )

    for item in products:
        item.final_price = get_price_by_discount(item)

    return render(
        request,
        'product_app/partials/last_products.html',
        {
            'products': products,
            'product_groups': get_root_group(),
            'group_sections': build_group_sections(
                request,
                '-register_date'
            )
        }
    )


def get_popular_product_groups(request, *args, **kwargs):
    product_groups = (
        ProductGroup.objects
        .filter(
            is_active=True
        )
        .annotate(
            count=Count(
                'products_of_groups',
                distinct=True
            )
        )
        .order_by(
            '-count'
        )[:6]
    )

    context = {
        'product_groups': product_groups
    }

    return render(
        request,
        'product_app/partials/popular_product_groups.html',
        context
    )


class StoreProductDetailView(View):

    def get(self, request, pk):
        store_product = get_object_or_404(
            StoreProduct.objects
            .select_related(
                'product',
                'product__brand',
                'store'
            )
            .prefetch_related(
                'product__gallery_images',
                'product__product_feature'
            ),
            pk=pk,
            is_active=True
        )

        user_score = 0

        if request.user.is_authenticated:
            user_score = get_user_score(
                store_product,
                request.user
            )

        return render(
            request,
            'product_app/product_detail.html',
            {
                'store_product': store_product,
                'user_score': user_score,
                'comment_form': CommentForm(
                    initial={'store_product_id': store_product.id}
                ),
            }
        )


def get_related_products(request, *args, **kwargs):
    current_product = get_object_or_404(
        Product,
        slug=kwargs['slug']
    )

    product_groups = current_product.product_group.all()

    related_products = (
        StoreProduct.objects
        .filter(
            product__product_group__in=product_groups,
            product__is_active=True,
            is_active=True,
            store__is_active=True
        )
        .exclude(
            product=current_product
        )
        .select_related(
            'product',
            'store'
        )
        .distinct()
    )

    return render(
        request,
        'product_app/partials/related_products.html',
        {
            'related_products': related_products
        }
    )


class ProductGroupsView(View):

    def get(self, request):
        product_groups = (
            ProductGroup.objects
            .filter(
                is_active=True
            )
            .annotate(
                count=Count(
                    'products_of_groups__store_products',
                    distinct=True
                )
            )
            .order_by(
                '-count'
            )
        )

        return render(
            request,
            'product_app/product_groups.html',
            {
                'product_groups': product_groups
            }
        )


def get_features_for_filter(request, *args, **kwargs):
    product_group = get_object_or_404(
        ProductGroup,
        slug=kwargs['slug']
    )

    feature_list = (
        product_group.features_of_groups
        .prefetch_related('feature_values')
    )

    feature_dict = {}

    for feature in feature_list:
        feature_dict[feature] = feature.feature_values.all()

    return render(
        request,
        'product_app/partials/feature_filter.html',
        {
            'feature_dict': feature_dict
        }
    )


def get_brands(request, *args, **kwargs):
    product_group = get_object_or_404(
        ProductGroup,
        slug=kwargs['slug']
    )

    group_ids = get_group_and_descendant_ids(product_group)

    active_brand_ids = (
        StoreProduct.objects
        .filter(
            product__product_group__in=group_ids,
            is_active=True
        )
        .values(
            'product__brand_id'
        )
    )

    brands = (
        Brand.objects
        .filter(
            id__in=active_brand_ids
        )
        .annotate(
            count=Count(
                'products_of_brands__store_products__store',
                filter=Q(
                    products_of_brands__product_group__in=group_ids,
                    products_of_brands__store_products__is_active=True
                ),
                distinct=True
            )
        )
        .filter(
            count__gt=0
        )
        .order_by(
            '-count'
        )
    )

    return render(
        request,
        'product_app/partials/brands.html',
        {
            'brands': brands
        }
    )


def get_stores(request, slug):
    product_group = get_object_or_404(
        ProductGroup,
        slug=slug
    )

    group_ids = get_group_and_descendant_ids(product_group)

    stores = (
        Store.objects
        .filter(
            products__product__product_group__in=group_ids,
            products__is_active=True,
            is_active=True
        )
        .annotate(
            count=Count(
                'products',
                filter=Q(
                    products__product__product_group__in=group_ids,
                    products__is_active=True
                ),
                distinct=True
            )
        )
        .distinct()
    )

    return render(
        request,
        'product_app/partials/stores.html',
        {
            'stores': stores
        }
    )


class ProductsByGroupView(View):

    def get(self, request, *args, **kwargs):
        current_group, products = get_products_by_group(
            kwargs['slug']
        )

        res_aggre = get_price_range(
            products
        )

        products, filter_obj = apply_product_filter(
            request.GET,
            products
        )

        brand_ids = request.GET.getlist('brand')

        products = apply_brand_filter(
            brand_ids,
            products
        )

        store_ids = request.GET.getlist('store')

        products = apply_store_filter(
            store_ids,
            products
        )

        feature_ids = request.GET.getlist('feature')

        products = apply_feature_filter(
            feature_ids,
            products
        )

        sort_type = request.GET.get(
            'sort_type',
            '0'
        )

        products = apply_sorting(
            sort_type,
            products
        )

        product_count = products.count()

        per_page = int(
            request.GET.get(
                'per_page',
                10
            )
        )

        page_number = request.GET.get('page')

        page_obj = paginate_products(
            page_number,
            per_page,
            products
        )

        # Options always start from the default (10), otherwise choosing 20
        # would remove 10 from the list and the visitor could not go back.
        # A fixed ladder is always offered, so the choice is usable even for a
        # small catalog; bigger catalogs add larger steps, and the current
        # choice is always part of the list.
        show_count_product = sorted(
            set(build_show_count_product(product_count, 10))
            | {5, 10, 20, 40}
            | {per_page}
        )

        # Pagination links must keep sorting, per-page and filters.
        query_params = request.GET.copy()
        query_params.pop('page', None)
        base_query = query_params.urlencode()

        if base_query:
            base_query += '&'

        context = {
            'products': products,
            'current_group': current_group,
            'res_aggre': res_aggre,
            'group_slug': kwargs['slug'],
            'page_obj': page_obj,
            'product_count': product_count,
            'show_count_product': show_count_product,
            'filter': filter_obj,
            'sort_type': sort_type,
            'per_page': per_page,
            'base_query': base_query
        }

        return render(
            request,
            'product_app/products.html',
            context
        )


def get_product_groups_menu(request):
    product_groups = ProductGroup.objects.filter(
        is_active=True,
        group_parent=None
    )

    return render(
        request,
        'product_app/partials/product_groups_menu.html',
        {
            'product_groups': product_groups
        }
    )


class CompareStoreProductView(View):

    def get(self, request, *args, **kwargs):
        compare_store_product = CompareStoreProduct(
            request
        )

        context = {
            'compare_store_product': compare_store_product
        }

        return render(
            request,
            'product_app/compare_store_list.html',
            context
        )


def compare_store_table(request):
    compare_list = CompareStoreProduct(
        request
    )

    store_products = (
        StoreProduct.objects
        .select_related(
            'product',
            'store'
        )
        .prefetch_related(
            'product__product_feature',
            'product__product_feature__feature',
            'product__product_feature__filter_value'
        )
        .filter(
            id__in=compare_list.compare_store_product
        )
    )

    features = []

    for store_product in store_products:
        for item in store_product.product.product_feature.all():
            if item.feature not in features:
                features.append(
                    item.feature
                )

    context = {
        'store_products': store_products,
        'features': features
    }

    return render(
        request,
        'product_app/partials/compare_store_table.html',
        context
    )


def add_store_product_to_compare(request):
    store_product_id = request.GET.get(
        'storeProductId'
    )

    get_object_or_404(
        StoreProduct,
        id=store_product_id
    )

    compare_list = CompareStoreProduct(
        request
    )

    compare_list.add(
        store_product_id
    )

    return HttpResponse(
        'به لیست مقایسه اضافه شد'
    )


def delete_store_product_from_compare(request):
    store_product_id = request.GET.get(
        'storeProductId'
    )

    compare_list = CompareStoreProduct(
        request
    )

    compare_list.remove(
        store_product_id
    )

    return redirect(
        'products:compare_store_table'
    )


def ajax_admin(request):
    """Feature values for the dependent dropdown in the admin product form."""
    if not request.user.is_staff:
        return JsonResponse({}, status=403)

    feature_id = request.GET.get('feature_id', '')

    if not feature_id.isdigit():
        return JsonResponse({})

    values = FeatureValue.objects.filter(feature_id=feature_id)

    return JsonResponse(
        {item.value_title: item.id for item in values}
    )


def get_nav_megamenu(request):
    return render(
        request,
        'product_app/partials/nav_megamenu.html',
        {
            'product_groups': get_root_group().prefetch_related('groups')
        }
    )
