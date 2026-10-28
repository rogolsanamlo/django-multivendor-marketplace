# Hand-written to match what `makemigrations` generates for this validator change.
# Only validators change, so no SQL is executed and no data is touched.

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comment_scoring_favorites', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoring',
            name='score',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
