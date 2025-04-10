# Generated by Django 5.1.7 on 2025-04-10 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_order_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Discount Amount'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Shipping Amount'),
        ),
        migrations.AddField(
            model_name='order',
            name='surcharge_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Surcharge Amount'),
        ),
        migrations.AddField(
            model_name='order',
            name='tax_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Tax Amount'),
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Total'),
        ),
    ]
