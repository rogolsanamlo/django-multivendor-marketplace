import utils

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.decorators.csrf import csrf_protect

from apps.orders.models import Order
from apps.payments.models import Payment

from .forms import (
    ChangePasswordForm,
    CreateStoreForm,
    EditStoreForm,
    LoginUserForm,
    RegisterUserForm,
    RememberPasswordForm,
    UpdateProfileForm,
    UpdateUserProfileForm,
    VerifyRegisterForm,
)
from .models import CustomUser, Store, UserProfile



@method_decorator(csrf_protect, name='dispatch')
class RegisterUserView(View):
    template_name = "accounts_app/register.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:index')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = RegisterUserForm()

        return render(
            request,
            self.template_name,
            {'form': form}
        )

    def post(self, request):
        form = RegisterUserForm(request.POST)

        if form.is_valid():
            try:
                active_code = utils.create_random_code(5)

                user = form.save(commit=False)
                user.active_code = active_code
                user.save()

                utils.send_sms(
                    user.mobile_number,
                    active_code
                )

                request.session['user_session'] = {
                    'active_code': str(active_code),
                    'mobile_number': user.mobile_number,
                    'remember_password': False
                }

                messages.success(
                    request,
                    'کد فعال‌سازی برای شما ارسال شد.'
                )

                return redirect('accounts:verify')

            except Exception:
                messages.error(
                    request,
                    'خطایی در ثبت‌نام رخ داد. لطفاً دوباره تلاش کنید.'
                )

        else:
            messages.error(
                request,
                'اطلاعات وارد شده صحیح نیست.'
            )

        return render(
            request,
            self.template_name,
            {'form': form}
        )


@method_decorator(csrf_protect, name='dispatch')
class LogoutUserView(LoginRequiredMixin, View):

    def post(self, request):
        # logout() flushes the session, which also empties the shop cart, so
        # the next person using this browser does not inherit it.
        logout(request)

        return redirect('main:index')


@method_decorator(csrf_protect, name='dispatch')
class LoginUserView(View):
    template_name = "accounts_app/login.html"

    def get(self, request):
        form = LoginUserForm()

        return render(
            request,
            self.template_name,
            {'form': form}
        )

    def post(self, request):
        form = LoginUserForm(request.POST)

        if form.is_valid():
            mobile_number = form.cleaned_data['mobile_number']
            password = form.cleaned_data['password']

            user = authenticate(
                username=mobile_number,
                password=password
            )

            if user:
                if not user.is_admin:
                    login(request, user)

                    next_url = request.GET.get('next')

                    if next_url and url_has_allowed_host_and_scheme(
                        next_url,
                        allowed_hosts={request.get_host()}
                    ):
                        return redirect(next_url)

                    return redirect('main:index')

                messages.error(
                    request,
                    'مدیر نمی‌تواند از این بخش وارد شود.'
                )

            else:
                messages.error(
                    request,
                    'شماره موبایل یا رمز عبور اشتباه است.'
                )

        else:
            messages.error(
                request,
                'اطلاعات وارد شده صحیح نیست.'
            )

        return render(
            request,
            self.template_name,
            {'form': form}
        )


@method_decorator(csrf_protect, name='dispatch')
class ChangePasswordView(View):
    template_name = "accounts_app/change_password.html"

    def get(self, request):
        form = ChangePasswordForm()

        return render(
            request,
            self.template_name,
            {'form': form}
        )

    def post(self, request):
        form = ChangePasswordForm(request.POST)

        if not form.is_valid():
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            })

        user_session = request.session.get('user_session')

        if not user_session:
            return JsonResponse({
                'status': 'error',
                'message': 'نشست شما منقضی شده است.'
            })

        if not user_session.get('verified'):
            return JsonResponse({
                'status': 'error',
                'message': 'ابتدا باید کد تأیید را وارد کنید.'
            })

        try:
            user = CustomUser.objects.get(
                mobile_number=user_session['mobile_number']
            )
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'کاربر پیدا نشد.'
            })

        user.set_password(
            form.cleaned_data['password1']
        )
        user.active_code = utils.create_random_code(5)
        user.save()
        request.session.pop('user_session', None)

        return JsonResponse({
            'status': 'success',
            'redirect_url': '/accounts/login/'
        })


@method_decorator(csrf_protect, name='dispatch')
class VerifyRegisterCodeView(View):
    template_name = "accounts_app/verify_register_code.html"

    def get(self, request):
        form = VerifyRegisterForm()

        return render(
            request,
            self.template_name,
            {'form': form}
        )

    def post(self, request):
        form = VerifyRegisterForm(request.POST)

        if form.is_valid():
            user_session = request.session.get('user_session')

            if not user_session:
                messages.error(
                    request,
                    'نشست شما منقضی شده است.'
                )
                return redirect('accounts:register')

            if form.cleaned_data['active_code'] == user_session['active_code']:
                try:
                    user = CustomUser.objects.get(
                        mobile_number=user_session['mobile_number']
                    )
                except CustomUser.DoesNotExist:
                    messages.error(
                        request,
                        'کاربر پیدا نشد.'
                    )
                    return redirect('accounts:register')

                if user_session['remember_password'] is False:
                    user.is_active = True
                    user.active_code = utils.create_random_code(5)
                    user.save()

                    messages.success(
                        request,
                        'ثبت‌نام شما با موفقیت انجام شد.'
                    )

                    return redirect('accounts:login')

                user_session['verified'] = True
                request.session['user_session'] = user_session

                messages.success(
                    request,
                    'کد تأیید شد. اکنون رمز عبور خود را تغییر دهید.'
                )

                return redirect('accounts:change_password')

            messages.error(
                request,
                'کد وارد شده صحیح نیست.'
            )

        return render(
            request,
            self.template_name,
            {'form': form}
        )


@method_decorator(csrf_protect, name='dispatch')
class RememberPasswordView(View):
    template_name = "accounts_app/remember_password.html"

    def get(self, request):
        form = RememberPasswordForm()

        return render(
            request,
            self.template_name,
            {'form': form}
        )

    def post(self, request):
        form = RememberPasswordForm(request.POST)

        if form.is_valid():
            mobile_number = form.cleaned_data['mobile_number']

            try:
                user = CustomUser.objects.get(
                    mobile_number=mobile_number
                )

                active_code = utils.create_random_code(5)
                user.active_code = active_code
                user.save()

                utils.send_sms(
                    user.mobile_number,
                    active_code
                )

                request.session['user_session'] = {
                    'active_code': str(active_code),
                    'mobile_number': user.mobile_number,
                    'remember_password': True
                }

                messages.success(
                    request,
                    'کد بازیابی رمز عبور برای شما ارسال شد.'
                )

                return redirect('accounts:verify')

            except CustomUser.DoesNotExist:
                messages.error(
                    request,
                    'کاربر پیدا نشد.'
                )

        return render(
            request,
            self.template_name,
            {'form': form}
        )


class UserPanelView(LoginRequiredMixin, View):
    template_name = "accounts_app/userpanel.html"

    def get(self, request):
        user = request.user
        profile = UserProfile.objects.filter(user=user).first()

        context = {
            'user': user,
            'profile': profile
        }

        return render(
            request,
            self.template_name,
            context
        )


class SellerDashboardView(LoginRequiredMixin, View):
    template_name = "accounts_app/seller_dashboard.html"

    def get(self, request):
        user = request.user
        profile = UserProfile.objects.filter(user=user).first()
        store = Store.objects.filter(user=user).first()

        if not store:
            return redirect('accounts:create_store')

        context = {
            'user': user,
            'profile': profile,
            'store': store
        }

        return render(
            request,
            self.template_name,
            context
        )


@method_decorator(csrf_protect, name='dispatch')
class UpdateProfileView(LoginRequiredMixin, View):
    template_name = "accounts_app/update_profile.html"

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user
        )

        user_form = UpdateProfileForm(
            instance=request.user
        )
        profile_form = UpdateUserProfileForm(
            instance=profile
        )

        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }

        return render(
            request,
            self.template_name,
            context
        )

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user
        )

        user_form = UpdateProfileForm(
            request.POST,
            instance=request.user
        )
        profile_form = UpdateUserProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()

            messages.success(
                request,
                'اطلاعات پروفایل با موفقیت بروزرسانی شد.'
            )

            return redirect('accounts:userpanel')

        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }

        return render(
            request,
            self.template_name,
            context
        )


@method_decorator(csrf_protect, name='dispatch')
class CreateStoreView(LoginRequiredMixin, View):
    template_name = "accounts_app/create_store.html"

    def get(self, request):
        if Store.objects.filter(user=request.user).exists():
            messages.warning(
                request,
                'شما قبلاً یک فروشگاه ثبت کرده‌اید.'
            )
            return redirect('accounts:edit_store')

        form = CreateStoreForm()

        return render(
            request,
            self.template_name,
            {'form': form}
        )

    def post(self, request):
        if Store.objects.filter(user=request.user).exists():
            messages.warning(
                request,
                'شما قبلاً یک فروشگاه ثبت کرده‌اید.'
            )
            return redirect('accounts:edit_store')

        form = CreateStoreForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()

            messages.success(
                request,
                'فروشگاه با موفقیت ثبت شد.'
            )

            return redirect('accounts:seller_dashboard')

        messages.error(
            request,
            'خطا در ثبت فروشگاه. لطفاً فیلدها را چک کنید.'
        )

        return render(
            request,
            self.template_name,
            {'form': form}
        )


@method_decorator(csrf_protect, name='dispatch')
class EditStoreView(LoginRequiredMixin, View):
    template_name = "accounts_app/edit_store.html"

    def get(self, request):
        store = Store.objects.filter(user=request.user).first()

        if store is None:
            messages.warning(
                request,
                'ابتدا فروشگاه خود را ثبت کنید.'
            )
            return redirect('accounts:create_store')

        form = EditStoreForm(instance=store)

        return render(
            request,
            self.template_name,
            {'form': form}
        )

    def post(self, request):
        store = Store.objects.filter(user=request.user).first()

        if store is None:
            messages.warning(
                request,
                'ابتدا فروشگاه خود را ثبت کنید.'
            )
            return redirect('accounts:create_store')

        form = EditStoreForm(
            request.POST,
            request.FILES,
            instance=store
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'اطلاعات فروشگاه با موفقیت بروزرسانی شد.'
            )

            return redirect('accounts:seller_dashboard')

        return render(
            request,
            self.template_name,
            {'form': form}
        )


class StoreDetailView(LoginRequiredMixin, View):
    template_name = "accounts_app/store_detail.html"

    def get(self, request):
        store = Store.objects.filter(user=request.user).first()

        if store is None:
            messages.warning(
                request,
                'ابتدا فروشگاه خود را ثبت کنید.'
            )
            return redirect('accounts:create_store')

        return render(
            request,
            self.template_name,
            {'store': store}
        )


@login_required
def show_last_orders(request):
    orders = Order.objects.filter(
        customer__user=request.user
    ).order_by('-register_date')[:4]

    return render(
        request,
        'accounts_app/show_last_orders.html',
        {'orders': orders}
    )


@login_required
def show_user_payments(request):
    payments = Payment.objects.filter(
        customer__user_id=request.user.id
    ).order_by('-register_date')

    return render(
        request,
        'accounts_app/show_user_payments.html',
        {'payments': payments}
    )