from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import SAFE_METHODS, AllowAny

from apps.api.pagination import OptionalPageNumberPagination
from apps.api.permissions import (
    IsAuthenticatedUser,
    IsStoreOwner,
)
from apps.api.serializers.products import (
    BrandSerializer,
    FeatureSerializer,
    FeatureValueSerializer,
    ProductFeatureSerializer,
    ProductGallerySerializer,
    ProductGroupSerializer,
    ProductSerializer,
    StoreProductSerializer,
)
from apps.products.models import (
    Brand,
    Feature,
    FeatureValue,
    Product,
    ProductFeature,
    ProductGallery,
    ProductGroup,
    StoreProduct,
)


class LegacyContextMixin:
    """
    ویوهای قبلی سریالایزر را بدون ``request`` می‌ساختند؛ برای اینکه
    خروجی (مثلاً آدرس تصویرها) تغییر نکند همان رفتار حفظ شده است.
    """

    def get_serializer_context(self):
        return {}


class BaseListAPIView(LegacyContextMixin, generics.ListAPIView):
    pagination_class = OptionalPageNumberPagination


class BaseDetailAPIView(LegacyContextMixin, generics.RetrieveAPIView):
    pass


# ---------------------------------------------------------------- Product


class ProductListAPIView(BaseListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_active=True)


class ProductDetailAPIView(BaseDetailAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(is_active=True)


# ----------------------------------------------------------- StoreProduct


class StoreProductPermissionsMixin:

    def get_permissions(self):

        if self.request.method in SAFE_METHODS:
            return []

        return [
            IsAuthenticatedUser(),
            IsStoreOwner(),
        ]


class StoreProductListAPIView(
    StoreProductPermissionsMixin,
    generics.ListCreateAPIView,
):
    serializer_class = StoreProductSerializer
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        return StoreProduct.objects.filter(
            is_active=True,
            store__is_active=True,
            product__is_active=True,
        )

    def perform_create(self, serializer):
        serializer.save(store=self.request.user.store)


class StoreProductDetailAPIView(
    StoreProductPermissionsMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = StoreProductSerializer

    def get_object(self):
        store_product = get_object_or_404(
            StoreProduct.objects.select_related("store", "product"),
            pk=self.kwargs["pk"],
        )

        is_public = (
            store_product.is_active
            and store_product.store.is_active
            and store_product.product.is_active
        )

        if not is_public:
            # خواندن کالای غیرفعال برای همه 404 است. نوشتن
            # (PUT/PATCH/DELETE) فقط برای صاحب کالا باز است تا بتواند
            # کالای غیرفعال خودش را دوباره فعال کند؛ بقیه ۴۰۴ می‌گیرند.
            is_owner = (
                store_product.store.user_id == self.request.user.id
            )

            if self.request.method in SAFE_METHODS or not is_owner:
                raise Http404

        self.check_object_permissions(self.request, store_product)

        return store_product

    def perform_destroy(self, instance):
        # حذف نرم: ردیف‌های انبار و خط‌های سفارش قدیمی (CASCADE)
        # دست نمی‌خورند و تاریخچه‌ی فروش حفظ می‌شود.
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active", "update_date"])


# ------------------------------------------------------- Read-only lists


class ProductGroupListAPIView(BaseListAPIView):
    serializer_class = ProductGroupSerializer
    queryset = ProductGroup.objects.filter(is_active=True)


class ProductGroupDetailAPIView(BaseDetailAPIView):
    serializer_class = ProductGroupSerializer
    queryset = ProductGroup.objects.filter(is_active=True)


class BrandListAPIView(BaseListAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()


class BrandDetailAPIView(BaseDetailAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()


class FeatureListAPIView(BaseListAPIView):
    serializer_class = FeatureSerializer
    queryset = Feature.objects.all()


class FeatureDetailAPIView(BaseDetailAPIView):
    serializer_class = FeatureSerializer
    queryset = Feature.objects.all()


class FeatureValueListAPIView(BaseListAPIView):
    serializer_class = FeatureValueSerializer
    queryset = FeatureValue.objects.all()


class FeatureValueDetailAPIView(BaseDetailAPIView):
    serializer_class = FeatureValueSerializer
    queryset = FeatureValue.objects.all()


class ProductFeatureListAPIView(BaseListAPIView):
    serializer_class = ProductFeatureSerializer
    queryset = ProductFeature.objects.all()


class ProductFeatureDetailAPIView(BaseDetailAPIView):
    serializer_class = ProductFeatureSerializer
    queryset = ProductFeature.objects.all()


class ProductGalleryListAPIView(BaseListAPIView):
    serializer_class = ProductGallerySerializer
    queryset = ProductGallery.objects.all()


class ProductGalleryDetailAPIView(BaseDetailAPIView):
    serializer_class = ProductGallerySerializer
    queryset = ProductGallery.objects.all()
