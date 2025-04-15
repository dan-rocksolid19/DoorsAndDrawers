from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base import BaseModel

class LineItem(BaseModel):
    ITEM_TYPE_CHOICES = [
        ('door', 'Door'),
        ('drawer', 'Drawer'),
        ('other', 'Other'),
    ]
    
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name="Order"
    )
    type = models.CharField(
        max_length=10,
        choices=ITEM_TYPE_CHOICES,
        default='other',
        verbose_name="Item Type"
    )
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Price per Unit"
    )
    custom_price = models.BooleanField(
        default=False,
        verbose_name="Custom Price",
        help_text="Indicates if the price has been manually adjusted"
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
    
    def calculate_price(self):
        """
        Abstract method to calculate the price per unit.
        Must be implemented by child classes.
        This should return the calculated price per unit only, ignoring any custom_price settings.
        """
        raise NotImplementedError("Subclasses must implement calculate_price()")
    
    @property
    def price(self):
        """
        Returns the total price of the item including quantity.
        If custom_price is True, uses the stored price_per_unit value.
        Otherwise, calls calculate_price() to get the calculated price per unit.
        """
        if self.custom_price:
            unit_price = self.price_per_unit
        else:
            unit_price = self.calculate_price()
            
        # Always multiply by quantity to get the total price
        return unit_price * self.quantity
        
    @property
    def total_price(self):
        """Calculate the total price for this line item"""
        return self.price
    
    def save(self, *args, **kwargs):
        """
        Override the save method to calculate and set the price_per_unit
        if custom_price is False. This ensures correct pricing regardless
        of how the model is instantiated.
        """
        if not self.custom_price:
            # Calculate and set the price_per_unit before saving
            self.price_per_unit = self.calculate_price()
        
        super().save(*args, **kwargs)

class GenericLineItem(LineItem):
    """
    Generic line item model for miscellaneous items, supplies, or charges.
    Uses the 'other' type in LineItem.
    """
    # Override the order field to use a specific related_name
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='generic_items',
        verbose_name="Order"
    )
    
    # Add name field for item description
    name = models.CharField(
        max_length=255,
        verbose_name="Item Name",
        help_text="Description of the item or service"
    )
    
    class Meta:
        verbose_name = "Miscellaneous Item"
        verbose_name_plural = "Miscellaneous Items"
    
    def calculate_price(self):
        """
        For generic items, there's no special calculation - just return the stored price_per_unit.
        """
        # For generic items, we simply return the price_per_unit directly
        return self.price_per_unit
    
    def __str__(self):
        return f"{self.name} - {self.quantity} × ${self.price_per_unit}"
    
    def save(self, *args, **kwargs):
        # Always set type to 'other'
        self.type = 'other'
        # Call the parent save method to handle price calculations
        super().save(*args, **kwargs) 