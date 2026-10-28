from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.views import View

import utils
from apps.accounts.models import CustomUser, UserProfile
from apps.discounts.forms import CouponForm
from apps.discounts.models import Coupon
from apps.products.models import StoreProduct

from .forms import OrderForm
from .models import (
    Order,
    OrderDetails,
    PaymentType,
)
from .shop_cart import ShopCart


class ShopCartView(View):

    def get(self, request, *args, **kwargs):
        shop_cart = ShopCart(request)

        return render(
            request,
            "orders_app/shop_cart.html",
            {
                "shop_cart": shop_cart,
            },
        )


def show_shop_cart(request):
    shop_cart = ShopCart(request)

    total_price = shop_cart.calc_total_price()

    order_final_price, delivery, tax = (
        utils.price_by_delivery_tax(
            total_price,
            0,
        )
    )

    context = {
        "shop_cart": shop_cart,
        "shop_cart_count": shop_cart.count,
        "total_price": total_price,
        "delivery": delivery,
        "tax": tax,
        "order_final_price": order_final_price,
    }

    return render(
        request,
        "orders_app/partials/show_shop_cart.html",
        context,
    )


def add_to_shop_cart(request):
    product_id = request.GET.get("product_id")

    if not (product_id or "").isdigit():
        raise Http404

    try:
        qty = int(request.GET.get("qty", 1))
    except (TypeError, ValueError):
        qty = 0

    if qty < 1:
        return HttpResponse(
            "تعداد کالا نامعتبر است",
            status=400,
        )

    shop_cart = ShopCart(request)

    store_product = get_object_or_404(
        StoreProduct,
        id=product_id,
        is_active=True,
    )

    added = shop_cart.add_to_shop_cart(
        store_product,
        qty,
    )

    if not added:
        return HttpResponse(
            "در هر خرید فقط می‌توانید از یک فروشگاه کالا انتخاب کنید",
            status=409,
        )

    return HttpResponse(
        shop_cart.count
    )


def delete_from_shop_cart(request):
    product_id = request.GET.get("product_id")

    store_product = get_object_or_404(
        StoreProduct,
        id=product_id,
    )

    shop_cart = ShopCart(request)

    shop_cart.delete_from_shop_cart(
        store_product
    )

    return redirect(
        "orders:show_shop_cart"
    )


def update_shop_cart(request):
    product_id_list = request.GET.getlist(
        "product_id_list[]"
    )

    qty_list = request.GET.getlist(
        "qty_list[]"
    )

    shop_cart = ShopCart(request)

    shop_cart.update(
        product_id_list,
        qty_list,
    )

    return redirect(
        "orders:show_shop_cart"
    )


def status_of_shop_cart(request):
    shop_cart = ShopCart(request)

    return HttpResponse(
        shop_cart.count
    )


class CreateOrderView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            customer = UserProfile.objects.get(
                user=request.user
            )
        except ObjectDoesNotExist:
            customer = UserProfile.objects.create(
                user=request.user
            )

        payment_type = PaymentType.objects.first()

        if not payment_type:
            payment_type = PaymentType.objects.create(
                payment_title="پرداخت آنلاین"
            )

        shop_cart = ShopCart(request)

        if shop_cart.count > 0:
            first_item = next(
                iter(shop_cart)
            )

            store = first_item[
                "store_product"
            ].store
        else:
            messages.error(
                request,
                "سبد خرید شما خالی است",
            )

            return redirect("orders:shop_cart")

        order = Order.objects.create(
            customer=customer,
            payment_type=payment_type,
            store=store,
        )

        for item in shop_cart:
            OrderDetails.objects.create(
                order=order,
                store_product=item[
                    "store_product"
                ],
                price=item["final_price"],
                qty=item["qty"],
            )

        return redirect(
            "orders:checkout_order",
            order.id,
        )


class CheckoutOrderView(LoginRequiredMixin, View):
    template_name = "orders_app/checkout.html"

    def get_customer_and_order(self, request, order_id):
        customer = get_object_or_404(
            UserProfile,
            user=request.user,
        )

        order = get_object_or_404(
            Order,
            id=order_id,
            customer=customer,
        )

        return customer, order

    def build_context(self, request, order, form):
        shop_cart = ShopCart(request)

        total_price = shop_cart.calc_total_price()

        order_final_price, delivery, tax = (
            utils.price_by_delivery_tax(
                total_price,
                order.discount or 0,
            )
        )

        return {
            "shop_cart": shop_cart,
            "total_price": total_price,
            "delivery": delivery,
            "tax": tax,
            "order_final_price": order_final_price,
            "form": form,
            "form_coupon": CouponForm(),
            "order": order,
        }

    def get(self, request, order_id):
        user = request.user

        customer, order = self.get_customer_and_order(
            request,
            order_id,
        )

        form = OrderForm(
            initial={
                "name": user.name,
                "family": user.family,
                "email": user.email,
                "phone_number": user.mobile_number,
                "address": customer.address,
                "description": order.description,
                "payment_type": order.payment_type_id,
            }
        )

        return render(
            request,
            self.template_name,
            self.build_context(request, order, form),
        )

    def post(self, request, order_id):
        user = request.user

        customer, order = self.get_customer_and_order(
            request,
            order_id,
        )

        form = OrderForm(request.POST)

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                self.build_context(request, order, form),
            )

        cleaned_data = form.cleaned_data

        order.description = cleaned_data["description"]
        order.payment_type = cleaned_data["payment_type"]
        order.save()

        user.name = cleaned_data["name"]
        user.family = cleaned_data["family"]
        user.email = cleaned_data["email"]

        mobile_conflict = False
        new_mobile = cleaned_data["phone_number"]

        if new_mobile and new_mobile != user.mobile_number:
            if (
                CustomUser.objects
                .filter(mobile_number=new_mobile)
                .exclude(pk=user.pk)
                .exists()
            ):
                mobile_conflict = True

                messages.error(
                    request,
                    "این شماره موبایل متعلق به کاربر دیگری است",
                    "danger",
                )
            else:
                user.mobile_number = new_mobile

        user.save()

        customer.address = cleaned_data["address"]
        customer.save()

        if mobile_conflict:
            return redirect(
                "orders:checkout_order",
                order_id,
            )

        return redirect(
            "payments:zarinpal_payment",
            order_id=order.id,
        )


class ApplyCoupon(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        order_id = kwargs["order_id"]

        coupon_form = CouponForm(
            request.POST
        )

        if coupon_form.is_valid():
            coupon_code = (
                coupon_form.cleaned_data[
                    "coupon_code"
                ]
            )

            coupon = Coupon.objects.filter(
                Q(coupon_code=coupon_code)
                & Q(is_active=True)
                & Q(start_date__lte=timezone.now())
                & Q(end_date__gte=timezone.now())
            ).first()

            discount = 0

            try:
                order = get_object_or_404(
                    Order,
                    id=order_id,
                    customer__user=request.user,
                )

                if coupon:
                    discount = coupon.discount
                    order.discount = discount
                    order.save()

                    messages.success(
                        request,
                        "اعمال کوپن با موفقیت انجام شد",
                    )

                    return redirect(
                        "orders:checkout_order",
                        order_id,
                    )

                order.discount = discount
                order.save()

                messages.error(
                    request,
                    "کد وارد شده معتبر نیست",
                    "danger",
                )

            except ObjectDoesNotExist:
                messages.error(
                    request,
                    "سفارش موجود نیست",
                )

        return redirect(
            "orders:checkout_order",
            order_id,
        )