# Generated by Django 5.1.7 on 2025-04-09 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_doorlineitem_design_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doorlineitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
