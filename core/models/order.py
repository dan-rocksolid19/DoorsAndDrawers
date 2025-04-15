from django.db import models
from itertools import chain
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
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Discount Amount"
    )
    surcharge_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Surcharge Amount"
    )
    shipping_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Shipping Amount"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Tax Amount"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Total"
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

    @property
    def order_number(self):
        """Generate order number based on type, date, and primary key"""
        prefix = 'QTE' if self.is_quote else 'ORD'
        date_str = self.order_date.strftime('%Y%m%d')
        pk_str = str(self.pk).zfill(4)  # Pad with zeros to 4 digits
        return f"{prefix}-{date_str}-{pk_str}"
    
    @property
    def line_items(self):
        """Get all line items for this order, regardless of type"""
        doors = self.door_items.all()
        drawers = self.drawer_items.all()
        return list(chain(doors, drawers))
    
    def get_line_items_by_type(self, item_type):
        """Get line items filtered by type"""
        if item_type == 'door':
            return self.door_items.all()
        elif item_type == 'drawer':
            return self.drawer_items.all()
        else:
            return []
    
    def count_total_items(self):
        """Count all line items"""
        return self.door_items.count() + self.drawer_items.count()
            
    def get_item_types_summary(self):
        """Get a summary of item types and counts"""
        return {
            'doors': self.door_items.count(),
            'drawers': self.drawer_items.count(),
            'total': self.count_total_items()
        }

    @property
    def item_total(self):
        """Calculate the sum of all line items"""
        door_total = sum(item.total_price for item in self.door_items.all())
        drawer_total = sum(item.total_price for item in self.drawer_items.all())
        return door_total + drawer_total

    @property
    def subtotal(self):
        """Calculate subtotal (item_total - discount + surcharge + shipping)"""
        return self.item_total - self.discount_amount + self.surcharge_amount + self.shipping_amount

    def calculate_totals(self):
        """Calculate and update all order totals based on customer defaults"""
        # Get customer defaults
        customer_defaults = self.customer.defaults
        
        # Calculate item total
        item_total = self.item_total
        
        # Calculate discount
        if customer_defaults.discount_type == 'PERCENT':
            self.discount_amount = item_total * (customer_defaults.discount_value / 100)
        else:
            self.discount_amount = customer_defaults.discount_value
        
        # Calculate surcharge
        if customer_defaults.surcharge_type == 'PERCENT':
            self.surcharge_amount = item_total * (customer_defaults.surcharge_value / 100)
        else:
            self.surcharge_amount = customer_defaults.surcharge_value
        
        # Calculate shipping
        if customer_defaults.shipping_type == 'PERCENT':
            self.shipping_amount = item_total * (customer_defaults.shipping_value / 100)
        else:
            self.shipping_amount = customer_defaults.shipping_value
        
        # Calculate total
        self.total = self.subtotal + self.tax_amount 