from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.orders.models import Order
from apps.products.models import StoreProduct
from apps.warehouses.models import Warehouse, WarehouseType

from .seller_forms import SellerStockForm, SellerStoreProductForm


class SellerRequiredMixin(LoginRequiredMixin):
    """Only logged-in users that own a store may use the seller pages."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            store = getattr(request.user, 'store', None)

            if store is None:
                messages.error(
                    request,
                    'برای استفاده از پنل فروشنده ابتدا فروشگاه خود را ثبت کنید.',
                )

                return redirect('accounts:create_store')

            self.store = store

        return super().dispatch(request, *args, **kwargs)


class SellerProductsView(SellerRequiredMixin, View):
    template_name = 'accounts_app/seller_products.html'

    def get(self, request):
        store_products = (
            StoreProduct.objects
            .filter(store=self.store)
            .select_related('product')
            .order_by('-register_date', '-id')
        )

        rows = [
            {
                'item': store_product,
                'stock': store_product.get_number_in_warehouse(),
            }
            for store_product in store_products
        ]

        return render(
            request,
            self.template_name,
            {'rows': rows, 'store': self.store},
        )


class SellerProductFormView(SellerRequiredMixin, View):
    template_name = 'accounts_app/seller_product_form.html'
    title = ''

    def get_instance(self, pk):
        return None

    def get(self, request, pk=None):
        instance = self.get_instance(pk)

        form = SellerStoreProductForm(
            instance=instance,
            store=self.store,
        )

        return render(
            request,
            self.template_name,
            {'form': form, 'title': self.title, 'instance': instance},
        )

    def post(self, request, pk=None):
        instance = self.get_instance(pk)

        form = SellerStoreProductForm(
            request.POST,
            instance=instance,
            store=self.store,
        )

        if form.is_valid():
            store_product = form.save(commit=False)
            store_product.store = self.store
            store_product.save()

            messages.success(request, 'کالای فروشگاه با موفقیت ذخیره شد.')

            return redirect('accounts:seller_products')

        return render(
            request,
            self.template_name,
            {'form': form, 'title': self.title, 'instance': instance},
        )


class SellerAddProductView(SellerProductFormView):
    title = 'افزودن کالا به فروشگاه'


class SellerEditProductView(SellerProductFormView):
    title = 'ویرایش کالای فروشگاه'

    def get_instance(self, pk):
        return get_object_or_404(
            StoreProduct,
            pk=pk,
            store=self.store,
        )


class SellerOrdersView(SellerRequiredMixin, View):
    template_name = 'accounts_app/seller_orders.html'

    def get(self, request):
        orders = list(
            Order.objects
            .filter(store=self.store, is_finally=True)
            .select_related('customer__user')
            .prefetch_related('details__store_product__product')
            .order_by('-register_date', '-id')[:100]
        )

        for order in orders:
            order.items_total = sum(
                detail.price * detail.qty
                for detail in order.details.all()
            )

        return render(
            request,
            self.template_name,
            {'orders': orders, 'store': self.store},
        )


class SellerStockView(SellerRequiredMixin, View):
    template_name = 'accounts_app/seller_stock.html'

    def build_context(self, form):
        store_products = (
            StoreProduct.objects
            .filter(store=self.store)
            .select_related('product')
            .order_by('product__product_name')
        )

        rows = [
            {
                'item': store_product,
                'stock': store_product.get_number_in_warehouse(),
            }
            for store_product in store_products
        ]

        entries = (
            Warehouse.objects
            .filter(store_product__store=self.store)
            .select_related('warehouse_type', 'store_product__product')
            .order_by('-register_date', '-id')[:20]
        )

        return {
            'form': form,
            'rows': rows,
            'entries': entries,
            'store': self.store,
        }

    def get(self, request):
        form = SellerStockForm(store=self.store)

        return render(
            request,
            self.template_name,
            self.build_context(form),
        )

    def post(self, request):
        form = SellerStockForm(request.POST, store=self.store)

        if form.is_valid():
            code = form.cleaned_data['movement']

            warehouse_type, _ = WarehouseType.objects.get_or_create(
                code=code,
                defaults={
                    'warehouse_type_title': dict(
                        SellerStockForm.MOVEMENT_CHOICES
                    )[code],
                },
            )

            Warehouse.objects.create(
                warehouse_type=warehouse_type,
                user_registered=request.user,
                store_product=form.cleaned_data['store_product'],
                qty=form.cleaned_data['qty'],
                price=form.cleaned_data['price'],
            )

            messages.success(request, 'موجودی انبار ثبت شد.')

            return redirect('accounts:seller_stock')

        return render(
            request,
            self.template_name,
            self.build_context(form),
        )
