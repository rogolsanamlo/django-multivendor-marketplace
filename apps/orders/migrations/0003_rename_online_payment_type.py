from django.db import migrations


def rename_online(apps, schema_editor):
    PaymentType = apps.get_model('orders', 'PaymentType')

    PaymentType.objects.filter(payment_title='Online').update(
        payment_title='پرداخت آنلاین'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_orderdetails_options'),
    ]

    operations = [
        migrations.RunPython(rename_online, migrations.RunPython.noop),
    ]
