from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import (
    Store,
    UserProfile,
)
from apps.api.permissions import IsAuthenticatedUser
from apps.api.serializers.accounts import (
    StoreSerializer,
    UserProfileSerializer,
    UserSerializer,
)


class UserProfileAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get(self, request):
        user = request.user

        profile = UserProfile.objects.filter(
            user=user
        ).first()

        user_serializer = UserSerializer(
            user
        )

        profile_serializer = (
            UserProfileSerializer(profile)
            if profile
            else None
        )

        return Response(
            {
                "user": user_serializer.data,
                "profile": (
                    profile_serializer.data
                    if profile_serializer
                    else None
                ),
            },
            status=status.HTTP_200_OK,
        )


class UpdateProfileAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user
        )

        user_serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=False,
        )

        profile_serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=False,
        )

        user_serializer.is_valid(
            raise_exception=True
        )

        profile_serializer.is_valid(
            raise_exception=True
        )

        user_serializer.save()
        profile_serializer.save()

        return Response(
            {
                "user": user_serializer.data,
                "profile": profile_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user
        )

        user_serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        profile_serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        user_serializer.is_valid(
            raise_exception=True
        )

        profile_serializer.is_valid(
            raise_exception=True
        )

        user_serializer.save()
        profile_serializer.save()

        return Response(
            {
                "user": user_serializer.data,
                "profile": profile_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class MyStoreAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get(self, request):
        store = get_object_or_404(
            Store,
            user=request.user,
        )

        serializer = StoreSerializer(
            store
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class CreateStoreAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def post(self, request):
        if Store.objects.filter(
            user=request.user
        ).exists():
            return Response(
                {
                    "detail": (
                        "شما قبلاً فروشگاه خود را ثبت کرده‌اید."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StoreSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        store = serializer.save(
            user=request.user
        )

        return Response(
            StoreSerializer(store).data,
            status=status.HTTP_201_CREATED,
        )


class UpdateStoreAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get_object(self, request):
        return get_object_or_404(
            Store,
            user=request.user,
        )

    def put(self, request):
        store = self.get_object(request)

        serializer = StoreSerializer(
            store,
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

    def patch(self, request):
        store = self.get_object(request)

        serializer = StoreSerializer(
            store,
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