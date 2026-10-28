from rest_framework.permissions import BasePermission


class IsAuthenticatedUser(BasePermission):

    def has_permission(self, request, view):

        return bool(
            request.user
            and request.user.is_authenticated
        )


class IsStoreOwner(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        store = getattr(
            request.user,
            "store",
            None
        )

        if store is None:
            return False

        return store.is_active

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):

        if not request.user.is_authenticated:
            return False

        store = getattr(
            request.user,
            "store",
            None
        )

        if store is None:
            return False

        if not store.is_active:
            return False

        if hasattr(obj, "store"):
            return obj.store.user == request.user

        if hasattr(obj, "store_product"):
            return (
                obj.store_product.store.user
                == request.user
            )

        return False