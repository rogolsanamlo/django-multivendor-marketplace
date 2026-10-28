from django.urls import path

from . import views


app_name = "products"


urlpatterns = [
    path(
        'cheapest_products/',
        views.get_cheapest_products,
        name='get_cheapest_products',
    ),
    path(
        'last_products/',
        views.get_last_products,
        name='get_last_products',
    ),
    path(
        'popular_product_groups/',
        views.get_popular_product_groups,
        name='get_popular_product_groups',
    ),
    path(
        'related_products/<slug:slug>/',
        views.get_related_products,
        name='get_related_products',
    ),
    path(
        'product_groups/',
        views.ProductGroupsView.as_view(),
        name='product_groups',
    ),
    path(
        'products_of_group/<slug:slug>/',
        views.ProductsByGroupView.as_view(),
        name='products_by_group',
    ),
    path(
        'product-details/<int:pk>/',
        views.StoreProductDetailView.as_view(),
        name='product_details',
    ),
    path(
        'features_for_filter/<slug:slug>/',
        views.get_features_for_filter,
        name='get_features_for_filter',
    ),
    path(
        'brands/<slug:slug>/',
        views.get_brands,
        name='get_brands',
    ),
    path(
        'stores/<slug:slug>/',
        views.get_stores,
        name='get_stores',
    ),
    path(
        'product_groups_menu/',
        views.get_product_groups_menu,
        name='get_product_groups_menu',
    ),
    path(
        'compare-store-table/',
        views.compare_store_table,
        name='compare_store_table',
    ),
    path(
        'compare-store-list/',
        views.CompareStoreProductView.as_view(),
        name='compare_store_list',
    ),
    path(
        'add-store-to-compare/',
        views.add_store_product_to_compare,
        name='add_store_product_to_compare',
    ),
    path(
        'delete-store-from-compare/',
        views.delete_store_product_from_compare,
        name='delete_store_product_from_compare',
    ),
    path(
        'nav_megamenu/',
        views.get_nav_megamenu,
        name='get_nav_megamenu',
    ),
    path(
        'ajax_admin/',
        views.ajax_admin,
        name='ajax_admin',
    ),
]