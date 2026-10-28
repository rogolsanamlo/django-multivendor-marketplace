from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'حساب‌های کاربری و فروشگاه‌ها'

    def ready(self):
        from . import signals  # noqa: F401  (registers the signal handlers)
