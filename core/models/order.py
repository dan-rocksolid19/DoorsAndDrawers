from django.db import models
from .base import BaseModel

class QuoteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_quote=True)

class ConfirmedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_quote=False)

class Order(BaseModel):
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Customer"
    )
    is_quote = models.BooleanField(
        default=False,
        verbose_name="Is Quote"
    )
    billing_address1 = models.CharField(
        max_length=255,
        verbose_name="Billing Address Line 1"
    )
    billing_address2 = models.CharField(
        max_length=255,
        verbose_name="Billing Address Line 2",
        blank=True
    )
    order_date = models.DateField(
        verbose_name="Order Date"
    )
    order_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Order Number"
    )

    # Managers
    objects = models.Manager()
    quotes = QuoteManager()
    confirmed = ConfirmedManager()

    class Meta:
        ordering = ['-order_date']
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        type_prefix = "Quote" if self.is_quote else "Order"
        return f"{type_prefix} {self.order_number} - {self.customer.company_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number if not provided
            order_date = self.order_date
            count_today = Order.objects.filter(order_date=order_date).count() + 1
            correlative = str(count_today).zfill(3)  # e.g., "001", "002", etc.
            prefix = 'QTE' if self.is_quote else 'ORD'
            self.order_number = f"{prefix}-{order_date.strftime('%Y%m%d')}-{correlative}"
        super().save(*args, **kwargs) 