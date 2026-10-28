from django.utils import timezone


def get_price_by_discount(store_product):

    discounts = []

    for item in store_product.discounts.all():

        basket = item.discount_basket

        if (
            basket.is_active
            and basket.start_date <= timezone.now()
            and timezone.now() <= basket.end_date
        ):
            discounts.append(
                basket.discount
            )

    max_discount = max(
        discounts,
        default=0
    )

    return (
        store_product.price
        - (
            store_product.price
            * max_discount
            / 100
        )
    )