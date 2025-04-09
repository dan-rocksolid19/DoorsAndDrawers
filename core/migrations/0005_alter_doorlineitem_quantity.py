# Generated by Django 5.1.7 on 2025-04-09 19:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_doorlineitem_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doorlineitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Quantity'),
        ),
    ]
