from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderdetails',
            options={'verbose_name': 'جزئیات سفارش', 'verbose_name_plural': 'جزئیات سفارش‌ها'},
        ),
    ]
