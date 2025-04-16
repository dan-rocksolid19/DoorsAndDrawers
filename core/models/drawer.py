from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .base import BaseModel
from .line_item import LineItem

class DrawerWoodStock(BaseModel):
    """Wood stock options for drawers"""
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Drawer Wood Stock'
        verbose_name_plural = 'Drawer Wood Stocks'

class DrawerEdgeType(BaseModel):
    """Edge types for drawers"""
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Drawer Edge Type'
        verbose_name_plural = 'Drawer Edge Types'

class DrawerBottomSize(BaseModel):
    """Bottom material types for drawers"""
    name = models.CharField(max_length=100, unique=True)
    thickness = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=1.000,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Drawer Bottom Type'
        verbose_name_plural = 'Drawer Bottom Types'

class DrawerPricing(BaseModel):
    """Base pricing configuration for drawers"""
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=50.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    class Meta:
        verbose_name = 'Drawer Pricing'
        verbose_name_plural = 'Drawer Pricing'
    
    def __str__(self):
        return f"Drawer Pricing Configuration (ID: {self.id})"

class DrawerLineItem(LineItem):
    """Drawer line item model"""
    # Override the order field to use a specific related_name
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='drawer_items',
        verbose_name="Order"
    )
    
    # Dimensions
    width = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Width in inches"
    )
    height = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Height in inches"
    )
    depth = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Depth in inches"
    )
    
    # Materials
    wood_stock = models.ForeignKey(
        DrawerWoodStock,
        on_delete=models.PROTECT,
        related_name='drawer_items'
    )
    edge_type = models.ForeignKey(
        DrawerEdgeType,
        on_delete=models.PROTECT,
        related_name='drawer_items'
    )
    bottom = models.ForeignKey(
        DrawerBottomSize,
        on_delete=models.PROTECT,
        related_name='drawer_items'
    )
    
    # Options
    undermount = models.BooleanField(
        default=False,
        help_text="Whether drawer uses undermount slides"
    )
    finishing = models.BooleanField(
        default=False,
        help_text="Whether drawer requires finishing"
    )
    
    class Meta:
        verbose_name = 'Drawer'
        verbose_name_plural = 'Drawers'
    
    def __str__(self):
        return f"{self.width}″ × {self.height}″ × {self.depth}″ Drawer"
    
    def calculate_price(self):
        """Calculate the unit price of the drawer based on dimensions and options"""
        # Get the base price from wood stock and bottom
        base_price = self.wood_stock.price + self.bottom.price
        
        # Get the default settings
        default_settings = DefaultDrawerSettings.objects.first()
        if not default_settings:
            return base_price
        
        # Add charges for options if enabled
        if self.undermount:
            base_price += default_settings.undermount_charge
            
        if self.finishing:
            base_price += default_settings.finish_charge
        
        return base_price
    
    def save(self, *args, **kwargs):
        # Always set type to 'drawer'
        self.type = 'drawer'
        # Call the parent save method to handle price calculations
        super().save(*args, **kwargs) 

class DefaultDrawerSettings(BaseModel):
    """Default settings and pricing adjustments for drawers"""
    surcharge_width = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Width surcharge for drawer pricing",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    surcharge_depth = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Depth surcharge for drawer pricing",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    surcharge_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage surcharge for drawer pricing",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    finish_charge = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Additional charge for finishing",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    undermount_charge = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Additional charge for undermount slides",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    ends_cutting_adjustment = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0.000,
        help_text="Adjustment for cutting drawer ends",
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    sides_cutting_adjustment = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0.000,
        help_text="Adjustment for cutting drawer sides",
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    plywood_size_adjustment = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0.000,
        help_text="Adjustment for plywood sizing",
        validators=[MinValueValidator(Decimal('0.000'))]
    )
    
    class Meta:
        verbose_name = 'Default Drawer Settings'
        verbose_name_plural = 'Default Drawer Settings'
    
    def __str__(self):
        return f"Default Drawer Settings (ID: {self.id})" 