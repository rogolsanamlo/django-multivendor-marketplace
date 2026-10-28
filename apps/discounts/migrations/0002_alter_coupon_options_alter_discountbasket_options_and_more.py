from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coupon',
            options={'verbose_name': 'کوپن تخفیف', 'verbose_name_plural': 'کوپن\u200cها'},
        ),
        migrations.AlterModelOptions(
            name='discountbasket',
            options={'verbose_name': 'سبد تخفیف', 'verbose_name_plural': 'سبدهای تخفیف'},
        ),
        migrations.AlterModelOptions(
            name='discountbasketdetails',
            options={'verbose_name': 'جزئیات سبد تخفیف', 'verbose_name_plural': 'جزئیات سبدهای تخفیف'},
        ),
    ]
