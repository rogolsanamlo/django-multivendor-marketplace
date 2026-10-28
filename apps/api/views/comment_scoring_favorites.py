from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import IsAuthenticatedUser
from apps.api.serializers.comment_scoring_favorites import (
    CommentSerializer,
    FavoriteSerializer,
    ScoringSerializer,
)
from apps.comment_scoring_favorites.models import (
    Comment,
    Favorite,
    Scoring,
)


class CommentListAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get(self, request):
        comments = Comment.objects.filter(
            is_active=True
        ).select_related(
            "store_product",
            "commenting_user",
        )

        serializer = CommentSerializer(
            comments,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = CommentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save(
            commenting_user=request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class CommentDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get_object(self, pk):
        return get_object_or_404(
            Comment,
            pk=pk,
            is_active=True,
        )

    def get(self, request, pk):
        comment = self.get_object(pk)

        serializer = CommentSerializer(
            comment
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        comment = self.get_object(pk)

        if comment.commenting_user != request.user:
            return Response(
                {
                    "detail": (
                        "شما اجازه ویرایش این نظر را ندارید."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CommentSerializer(
            comment,
            data=request.data,
            partial=False,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        comment = self.get_object(pk)

        if comment.commenting_user != request.user:
            return Response(
                {
                    "detail": (
                        "شما اجازه ویرایش این نظر را ندارید."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CommentSerializer(
            comment,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        comment = self.get_object(pk)

        if comment.commenting_user != request.user:
            return Response(
                {
                    "detail": (
                        "شما اجازه حذف این نظر را ندارید."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class ScoringListAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get(self, request):
        scores = Scoring.objects.all().select_related(
            "store_product",
            "scoring_user",
        )

        serializer = ScoringSerializer(
            scores,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ScoringSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        store_product = serializer.validated_data[
            "store_product"
        ]

        scoring, created = Scoring.objects.update_or_create(
            store_product=store_product,
            scoring_user=request.user,
            defaults={
                "score": serializer.validated_data["score"],
            },
        )

        result_serializer = ScoringSerializer(
            scoring
        )

        return Response(
            result_serializer.data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )


class ScoringDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get_object(self, pk):
        return get_object_or_404(
            Scoring,
            pk=pk,
        )

    def get(self, request, pk):
        scoring = self.get_object(pk)

        serializer = ScoringSerializer(
            scoring
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        scoring = self.get_object(pk)

        if scoring.scoring_user != request.user:
            return Response(
                {
                    "detail": (
                        "شما اجازه ویرایش این امتیاز را ندارید."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ScoringSerializer(
            scoring,
            data=request.data,
            partial=False,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        scoring = self.get_object(pk)

        if scoring.scoring_user != request.user:
            return Response(
                {
                    "detail": (
                        "شما اجازه ویرایش این امتیاز را ندارید."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ScoringSerializer(
            scoring,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        scoring = self.get_object(pk)

        if scoring.scoring_user != request.user:
            return Response(
                {
                    "detail": (
                        "شما اجازه حذف این امتیاز را ندارید."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        scoring.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class FavoriteListAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get(self, request):
        favorites = Favorite.objects.filter(
            favorite_user=request.user
        ).select_related(
            "store_product",
            "store_product__product",
            "store_product__store",
        )

        serializer = FavoriteSerializer(
            favorites,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = FavoriteSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        store_product = serializer.validated_data[
            "store_product"
        ]

        favorite, created = Favorite.objects.get_or_create(
            store_product=store_product,
            favorite_user=request.user,
        )

        result_serializer = FavoriteSerializer(
            favorite
        )

        if not created:
            return Response(
                {
                    "detail": (
                        "این کالا قبلاً در لیست علاقه‌مندی‌ها "
                        "قرار دارد."
                    ),
                    "data": result_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            result_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class FavoriteDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get_object(self, pk):
        return get_object_or_404(
            Favorite,
            pk=pk,
        )

    def get(self, request, pk):
        favorite = self.get_object(pk)

        if favorite.favorite_user != request.user:
            return Response(
                {
                    "detail": (
                        "شما اجازه دسترسی به این "
                        "علاقه‌مندی را ندارید."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = FavoriteSerializer(
            favorite
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        favorite = self.get_object(pk)

        if favorite.favorite_user != request.user:
            return Response(
                {
                    "detail": (
                        "شما اجازه حذف این علاقه‌مندی "
                        "را ندارید."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        favorite.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )