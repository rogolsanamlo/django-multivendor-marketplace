from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views import View

from apps.products.models import StoreProduct

from .forms import CommentForm
from .models import Comment, Favorite, Scoring


class CommentView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        store_product_id = request.GET.get(
            "storeProductId"
        )
        comment_id = request.GET.get(
            "commentId"
        )
        slug = kwargs["slug"]

        initial_dict = {
            "store_product_id": store_product_id,
            "comment_id": comment_id,
        }

        form = CommentForm(
            initial=initial_dict
        )

        return render(
            request,
            "csf_app/partials/create_comment.html",
            {
                "form": form,
                "slug": slug,
            },
        )

    def post(self, request, *args, **kwargs):
        slug = kwargs.get("slug")

        form = CommentForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            store_product = get_object_or_404(
                StoreProduct,
                id=cleaned_data["store_product_id"],
            )

            parent = None

            if cleaned_data["comment_id"]:
                parent = get_object_or_404(
                    Comment,
                    id=cleaned_data["comment_id"],
                )

            Comment.objects.create(
                store_product=store_product,
                commenting_user=request.user,
                comment_text=cleaned_data["comment_text"],
                comment_parent=parent,
            )

            messages.success(
                request,
                "نظر شما ثبت شد و پس از تأیید مدیر نمایش داده می‌شود",
            )

            return redirect(
                "products:product_details",
                pk=store_product.id,
            )

        messages.error(
            request,
            "نظر ارسال نشد؛ متن نظر را وارد کنید.",
        )

        store_product = None
        store_product_id = form.cleaned_data.get("store_product_id")

        if store_product_id:
            store_product = (
                StoreProduct.objects
                .select_related("product")
                .filter(id=store_product_id)
                .first()
            )

        if store_product is None:
            return redirect("main:index")

        return redirect(
            "products:product_details",
            pk=store_product.id,
        )


def add_score(request):
    if not request.user.is_authenticated:
        return HttpResponse(
            "برای ثبت امتیاز باید وارد شوید",
            status=401,
        )

    store_product_id = request.GET.get(
        "storeProductId"
    )
    score = request.GET.get(
        "score"
    )

    if score not in {"1", "2", "3", "4", "5"}:
        return HttpResponse(
            "امتیاز باید عددی بین ۱ تا ۵ باشد",
            status=400,
        )

    store_product = get_object_or_404(
        StoreProduct,
        id=store_product_id,
    )

    Scoring.objects.update_or_create(
        store_product=store_product,
        scoring_user=request.user,
        defaults={
            "score": score,
        },
    )

    return JsonResponse({
        "message": "امتیاز شما با موفقیت ثبت شد",
        "average": round(store_product.get_average_score(), 1),
    })


def add_to_favorite(request):
    if not request.user.is_authenticated:
        return HttpResponse(
            "برای افزودن به علاقه‌مندی‌ها باید وارد شوید",
            status=401,
        )

    store_product_id = request.GET.get(
        "storeProductId"
    )

    store_product = get_object_or_404(
        StoreProduct,
        id=store_product_id,
    )

    flag = Favorite.objects.filter(
        favorite_user_id=request.user.id,
        store_product_id=store_product.id,
    ).exists()

    if not flag:
        Favorite.objects.create(
            store_product=store_product,
            favorite_user=request.user,
        )

        return HttpResponse(
            "این کالا به لیست علایق شما اضافه شد"
        )

    return HttpResponse(
        "این کالا قبلا در لیست علایق شما قرار دارد "
    )


def delete_from_favorite(request):
    if not request.user.is_authenticated:
        return HttpResponse(
            "برای این کار باید وارد شوید",
            status=401,
        )

    store_product_id = request.GET.get("storeProductId")

    Favorite.objects.filter(
        favorite_user=request.user,
        store_product_id=store_product_id,
    ).delete()

    return HttpResponse("این کالا از لیست علایق شما حذف شد")


class UserFavoriteView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user_favorite_products = (
            Favorite.objects
            .select_related(
                "store_product",
                "store_product__product",
                "store_product__store",
            )
            .filter(
                favorite_user=request.user
            )
        )

        return render(
            request,
            "csf_app/user_favorite.html",
            {
                "user_favorite_products": (
                    user_favorite_products
                ),
            },
        )