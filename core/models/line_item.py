from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import BaseModel

class LineItem(BaseModel):
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='line_items',
        verbose_name="Order"
    )
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Price per Unit"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Quantity"
    )

    class Meta:
        abstract = True
        verbose_name = "Line Item"
        verbose_name_plural = "Line Items"
        ordering = ['-created_at']

    def __str__(self):
        return f"Line Item {self.id} - Order {self.order.order_number}"

    @property
    def total_price(self):
        """Calculate the total price for this line item"""
        return self.price_per_unit * self.quantity 