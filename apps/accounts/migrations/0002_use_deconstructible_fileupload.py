import utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=utils.FileUpload('images', 'logo'), verbose_name='لوگو'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='image_name',
            field=models.ImageField(blank=True, null=True, upload_to=utils.FileUpload('images', 'customer'), verbose_name='تصویر پروفایل'),
        ),
    ]
