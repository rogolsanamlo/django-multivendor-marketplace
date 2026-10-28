from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_use_deconstructible_fileupload'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'کاربر', 'verbose_name_plural': 'کاربران'},
        ),
        migrations.AlterModelOptions(
            name='store',
            options={'verbose_name': 'فروشگاه', 'verbose_name_plural': 'فروشگاه‌ها'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'پروفایل کاربر', 'verbose_name_plural': 'پروفایل‌های کاربران'},
        ),
    ]
