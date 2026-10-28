import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views import View

from apps.orders.models import Order
from apps.warehouses.models import Warehouse, WarehouseType

from .models import Payment
from zarinpal import ZarinPal

logger = logging.getLogger(__name__)


class Config:

    """Settings object read by the zarinpal-py-sdk (``ZarinPal(config)``)."""

    def __init__(self, sandbox, merchant_id, access_token=""):
        self.sandbox = sandbox
        self.merchant_id = merchant_id
        # The SDK reads this attribute when it is created; it is only needed
        # for ZarinPal's reporting API, not for payment requests.
        self.access_token = access_token


def debug_detail(detail):
    """Technical details are shown only while DEBUG is on (development)."""
    return f" [{detail}]" if settings.DEBUG else ""


def redirect_to_payment_message(request, message):
    request.session["payment_message"] = message

    return redirect(
        "payments:show_verify_message"
    )


def finalize_order(order):
    """Mark a paid order as final and take its items out of the stock.

    Stock is a ledger (input minus output rows), so "decreasing" it means
    adding one ``output`` row per order line. This runs only on the
    not-final -> final transition: a repeated callback (ZarinPal answers
    101 on a second verify) finds the order already final and does nothing,
    so stock is never decreased twice for the same order.
    """
    with transaction.atomic():
        # Lock the row so two simultaneous callbacks cannot both pass the check.
        order = Order.objects.select_for_update().get(pk=order.pk)

        if order.is_finally:
            return False

        output_type, _ = WarehouseType.objects.get_or_create(
            code=WarehouseType.OUTPUT,
            defaults={"warehouse_type_title": "خروج از انبار"},
        )

        for detail in order.details.select_related("store_product"):
            Warehouse.objects.create(
                warehouse_type=output_type,
                user_registered=order.customer.user,
                store_product=detail.store_product,
                qty=detail.qty,
            )

        order.is_finally = True
        order.save()

    return True


class ZarinPalPaymentView(LoginRequiredMixin, View):

    def get(self, request, order_id):
        user = request.user

        order = get_object_or_404(
            Order,
            id=order_id,
            customer__user=user,
        )

        if not order.customer.address:
            messages.error(
                request,
                "برای ثبت سفارش ابتدا اطلاعات و آدرس خود را تکمیل کنید",
            )

            return redirect(
                "orders:checkout_order",
                order.id,
            )

        if order.is_finally:
            return redirect_to_payment_message(
                request,
                "این سفارش قبلاً پرداخت شده است.",
            )

        amount = order.get_order_total_price()

        payment = Payment.objects.create(
            order=order,
            customer=order.customer,
            amount=amount,
            description="پرداخت از طریق درگاه زرین پال",
        )

        request.session["payment_session"] = {
            "order_id": order.id,
            "payment_id": payment.id,
        }

        try:
            config = Config(
                sandbox=settings.ZARINPAL_SANDBOX,
                merchant_id=settings.ZARINPAL_MERCHANT_ID,
                access_token=settings.ZARINPAL_ACCESS_TOKEN,
            )

            zarinpal = ZarinPal(config)

            payload = {
                "amount": amount,
                "callback_url": settings.ZARINPAL_CALLBACK_URL,
                "description": "پرداخت از طریق درگاه زرین پال",
                "currency": "IRR",
            }

            if user.mobile_number:
                payload["mobile"] = user.mobile_number

            if user.email:
                payload["email"] = user.email

            response = zarinpal.payments.create(payload)

            if "data" not in response:
                logger.error("ZarinPal create payment failed: %s", response)

                return redirect_to_payment_message(
                    request,
                    "خطا در ایجاد درخواست پرداخت."
                    + debug_detail(response),
                )

            authority = response["data"].get(
                "authority"
            )

            if not authority:
                return redirect_to_payment_message(
                    request,
                    "Authority از زرین پال دریافت نشد.",
                )

            payment.authority = authority
            payment.save()

            payment_url = (
                zarinpal.payments.generate_payment_url(
                    authority
                )
            )

            return redirect(payment_url)

        except Exception as e:
            logger.exception("ZarinPal payment request failed")

            return redirect_to_payment_message(
                request,
                "خطا در ارتباط با درگاه پرداخت. لطفاً دوباره تلاش کنید."
                + debug_detail(f"{type(e).__name__}: {e}"),
            )


class ZarinPalPaymentVerifyView(
    LoginRequiredMixin,
    View,
):

    def get(self, request):
        status = request.GET.get("Status")
        authority = request.GET.get("Authority")

        if status != "OK":
            return redirect_to_payment_message(
                request,
                "پرداخت توسط کاربر لغو شد یا ناموفق بود.",
            )

        payment = get_object_or_404(
            Payment,
            authority=authority,
            customer__user=request.user,
        )

        order = payment.order
        amount = payment.amount

        try:
            config = Config(
                sandbox=settings.ZARINPAL_SANDBOX,
                merchant_id=settings.ZARINPAL_MERCHANT_ID,
                access_token=settings.ZARINPAL_ACCESS_TOKEN,
            )

            zarinpal = ZarinPal(config)

            response = zarinpal.verifications.verify(
                {
                    "amount": amount,
                    "authority": authority,
                }
            )

            status_code = response["data"]["code"]

            if status_code == 100:
                payment.is_finally = True
                payment.status_code = status_code
                payment.ref_id = str(
                    response["data"]["ref_id"]
                )
                payment.save()

                finalize_order(order)

                request.session.pop("shop_cart", None)

                return redirect_to_payment_message(
                    request,
                    (
                        "پرداخت با موفقیت انجام شد. "
                        f"کد رهگیری: {payment.ref_id}"
                    ),
                )

            elif status_code == 101:
                payment.is_finally = True
                payment.status_code = status_code
                payment.ref_id = str(
                    response["data"].get("ref_id", "")
                )
                payment.save()

                finalize_order(order)

                return redirect_to_payment_message(
                    request,
                    "این پرداخت قبلاً تأیید شده است.",
                )

            else:
                payment.status_code = status_code
                payment.save()

                return redirect_to_payment_message(
                    request,
                    (
                        "پرداخت ناموفق بود. "
                        f"کد وضعیت: {status_code}"
                    ),
                )

        except Exception as e:
            logger.exception("ZarinPal payment verification failed")

            return redirect_to_payment_message(
                request,
                "خطا در تأیید پرداخت. در صورت کسر وجه با پشتیبانی تماس بگیرید."
                + debug_detail(f"{type(e).__name__}: {e}"),
            )


def show_verify_message(request):
    message = request.session.pop(
        "payment_message",
        "نتیجه‌ای برای پرداخت وجود ندارد.",
    )

    return render(
        request,
        "payments_app/verify_message.html",
        {
            "message": message,
        },
    )