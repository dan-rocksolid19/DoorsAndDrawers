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
        """Calculate the price of the drawer based on dimensions and options"""
        # Base calculation from dimensions
        return self.wood_stock.price + self.bottom.price
    
    def save(self, *args, **kwargs):
        # Update price if not custom
        # if not self.custom_price:
        #     self.price = self.calculate_price()
        
        super().save(*args, **kwargs) 