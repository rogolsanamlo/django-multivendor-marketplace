from apps.products.models import StoreProduct
from apps.discounts.services import get_price_by_discount


class ShopCart:

    def __init__(self, request):
        self.session = request.session

        temp = self.session.get("shop_cart")

        if not temp:
            temp = self.session["shop_cart"] = {}

        self.shop_cart = temp

        self.count = len(
            self.shop_cart.keys()
        )

    def add_to_shop_cart(
        self,
        store_product,
        qty,
    ):
        if self.shop_cart:
            first_id = list(
                self.shop_cart.keys()
            )[0]

            first_store_product = (
                StoreProduct.objects
                .select_related("store")
                .get(id=first_id)
            )

            if (
                first_store_product.store_id
                != store_product.store_id
            ):
                return False

        store_product_id = str(
            store_product.id
        )

        if store_product_id not in self.shop_cart:
            self.shop_cart[store_product_id] = {
                "qty": 0,
                "price": int(store_product.price),
                "final_price": int(
                    get_price_by_discount(store_product)
                ),
            }

        self.shop_cart[store_product_id]["qty"] += int(qty)

        self.count = len(
            self.shop_cart.keys()
        )

        self.save()

        return True

    def delete_from_shop_cart(
        self,
        store_product,
    ):
        store_product_id = str(
            store_product.id
        )

        self.shop_cart.pop(
            store_product_id,
            None,
        )

        self.save()

    def update(
        self,
        product_id_list,
        qty_list,
    ):
        i = 0

        for product_id in product_id_list:
            if product_id in self.shop_cart:
                self.shop_cart[product_id]["qty"] = int(
                    qty_list[i]
                )
            i += 1

        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        list_id = self.shop_cart.keys()

        store_products = (
            StoreProduct.objects
            .select_related(
                "product",
                "store",
            )
            .filter(
                id__in=list_id
            )
        )

        temp = {
            key: dict(value)
            for key, value in self.shop_cart.items()
        }

        for store_product in store_products:
            temp[
                str(store_product.id)
            ]["store_product"] = store_product

        for item in temp.values():
            item["total_price"] = (
                item["final_price"]
                * item["qty"]
            )

            yield item

    def calc_total_price(self):
        total = 0

        for item in self.shop_cart.values():
            total += int(
                item["final_price"]
                * item["qty"]
            )

        return total