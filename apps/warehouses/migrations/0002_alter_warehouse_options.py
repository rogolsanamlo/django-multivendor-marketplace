from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='warehouse',
            options={'verbose_name': 'انبار', 'verbose_name_plural': 'انبارها'},
        ),
    ]
