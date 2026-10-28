from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

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


class ProductListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.filter(
            is_active=True
        )

        serializer = ProductSerializer(
            products,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product = get_object_or_404(
            Product,
            pk=pk,
            is_active=True
        )

        serializer = ProductSerializer(
            product
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class StoreProductListAPIView(APIView):

    def get_permissions(self):

        if self.request.method == "GET":
            return []

        return [
            IsAuthenticatedUser(),
            IsStoreOwner(),
        ]

    def get(self, request):
        store_products = StoreProduct.objects.filter(
            is_active=True,
            store__is_active=True,
            product__is_active=True
        )

        serializer = StoreProductSerializer(
            store_products,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = StoreProductSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        store_product = serializer.save(
            store=request.user.store
        )

        return Response(
            StoreProductSerializer(
                store_product,
                context={
                    "request": request
                }
            ).data,
            status=status.HTTP_201_CREATED
        )


class StoreProductDetailAPIView(APIView):

    def get_permissions(self):

        if self.request.method in [
            "GET",
            "HEAD",
            "OPTIONS",
        ]:
            return []

        return [
            IsAuthenticatedUser(),
            IsStoreOwner(),
        ]

    def get_object(self, pk):
        return get_object_or_404(
            StoreProduct,
            pk=pk,
            is_active=True,
            store__is_active=True,
            product__is_active=True
        )

    def get(self, request, pk):
        store_product = self.get_object(pk)

        serializer = StoreProductSerializer(
            store_product,
            context={
                "request": request
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        store_product = self.get_object(pk)

        self.check_object_permissions(
            request,
            store_product
        )

        serializer = StoreProductSerializer(
            store_product,
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        store_product = serializer.save()

        return Response(
            StoreProductSerializer(
                store_product,
                context={
                    "request": request
                }
            ).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        store_product = self.get_object(pk)

        self.check_object_permissions(
            request,
            store_product
        )

        serializer = StoreProductSerializer(
            store_product,
            data=request.data,
            partial=True,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        store_product = serializer.save()

        return Response(
            StoreProductSerializer(
                store_product,
                context={
                    "request": request
                }
            ).data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        store_product = self.get_object(pk)

        self.check_object_permissions(
            request,
            store_product
        )

        store_product.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ProductGroupListAPIView(APIView):

    def get(self, request):
        groups = ProductGroup.objects.filter(
            is_active=True
        )

        serializer = ProductGroupSerializer(
            groups,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductGroupDetailAPIView(APIView):

    def get(self, request, pk):
        group = get_object_or_404(
            ProductGroup,
            pk=pk,
            is_active=True
        )

        serializer = ProductGroupSerializer(
            group
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class BrandListAPIView(APIView):

    def get(self, request):
        brands = Brand.objects.all()

        serializer = BrandSerializer(
            brands,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class BrandDetailAPIView(APIView):

    def get(self, request, pk):
        brand = get_object_or_404(
            Brand,
            pk=pk
        )

        serializer = BrandSerializer(
            brand
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class FeatureListAPIView(APIView):

    def get(self, request):
        features = Feature.objects.all()

        serializer = FeatureSerializer(
            features,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class FeatureDetailAPIView(APIView):

    def get(self, request, pk):
        feature = get_object_or_404(
            Feature,
            pk=pk
        )

        serializer = FeatureSerializer(
            feature
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class FeatureValueListAPIView(APIView):

    def get(self, request):
        values = FeatureValue.objects.all()

        serializer = FeatureValueSerializer(
            values,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class FeatureValueDetailAPIView(APIView):

    def get(self, request, pk):
        value = get_object_or_404(
            FeatureValue,
            pk=pk
        )

        serializer = FeatureValueSerializer(
            value
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductFeatureListAPIView(APIView):

    def get(self, request):
        product_features = ProductFeature.objects.all()

        serializer = ProductFeatureSerializer(
            product_features,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductFeatureDetailAPIView(APIView):

    def get(self, request, pk):
        product_feature = get_object_or_404(
            ProductFeature,
            pk=pk
        )

        serializer = ProductFeatureSerializer(
            product_feature
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductGalleryListAPIView(APIView):

    def get(self, request):
        galleries = ProductGallery.objects.all()

        serializer = ProductGallerySerializer(
            galleries,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ProductGalleryDetailAPIView(APIView):

    def get(self, request, pk):
        gallery = get_object_or_404(
            ProductGallery,
            pk=pk
        )

        serializer = ProductGallerySerializer(
            gallery
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )