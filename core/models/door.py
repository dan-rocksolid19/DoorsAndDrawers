from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

from .base import BaseModel
from .line_item import LineItem


class WoodStock(BaseModel):
    """Model for wood stock options (materials) for doors."""
    name = models.CharField(max_length=50, unique=True)
    raised_panel_price = models.DecimalField(max_digits=10, decimal_places=2)
    flat_panel_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name


class Design(BaseModel):
    """Model for door designs."""
    name = models.CharField(max_length=50, unique=True)
    arch = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class EdgeProfile(BaseModel):
    """Model for door edge profiles."""
    name = models.CharField(max_length=10, unique=True)  # E1, E2, etc.
    
    def __str__(self):
        return self.name


class PanelType(BaseModel):
    """Model for door panel types."""
    name = models.CharField(max_length=50, unique=True)
    surcharge_width = models.DecimalField(max_digits=5, decimal_places=2)
    surcharge_height = models.DecimalField(max_digits=5, decimal_places=2)
    surcharge_percent = models.DecimalField(max_digits=5, decimal_places=2)
    minimum_sq_ft = models.DecimalField(max_digits=5, decimal_places=2)
    use_flat_panel_price = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class PanelRise(BaseModel):
    """Model for panel rise options."""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name


class Style(BaseModel):
    """Model for door styles."""
    name = models.CharField(max_length=50, unique=True)  # ATFP, CTF, etc.
    panel_type = models.ForeignKey(PanelType, on_delete=models.PROTECT)
    design = models.ForeignKey(Design, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    panels_across = models.PositiveSmallIntegerField(default=1)
    panels_down = models.PositiveSmallIntegerField(default=1)
    panel_overlap = models.DecimalField(max_digits=5, decimal_places=3)
    designs_on_top = models.BooleanField(default=False)
    designs_on_bottom = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.panel_type.name} - {self.design.name}"


class DoorLineItem(LineItem):
    """Model for door line items with all settings."""
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='door_items',
        verbose_name="Order"
    )
    
    wood_stock = models.ForeignKey(WoodStock, on_delete=models.PROTECT)
    edge_profile = models.ForeignKey(EdgeProfile, on_delete=models.PROTECT)
    panel_rise = models.ForeignKey(PanelRise, on_delete=models.PROTECT, null=True, blank=True)
    style = models.ForeignKey(Style, on_delete=models.PROTECT)

    # Door dimensions
    width = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Width in inches"
    )
    height = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Height in inches"
    )
    
    # Rail dimensions
    rail_top = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Top rail size in inches",
        default=Decimal('1.000')
    )
    rail_bottom = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Bottom rail size in inches",
        default=Decimal('1.000')
    )
    rail_left = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Left rail size in inches",
        default=Decimal('1.000')
    )
    rail_right = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Right rail size in inches",
        default=Decimal('1.000')
    )
    interior_rail_size = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Interior rail size in inches",
        default=Decimal('1.000')
    )

    # Sanding options
    sand_edge = models.BooleanField(
        default=False,
        help_text="Whether to sand the edges of the door"
    )
    sand_cross_grain = models.BooleanField(
        default=False,
        help_text="Whether to sand across the grain"
    )
    
    class Meta:
        verbose_name = "Door Item"
        verbose_name_plural = "Door Items"
    
    @property
    def square_feet(self):
        """Calculate the square footage of the door."""
        return (self.width * self.height) / 144  # Convert to square feet

    def calculate_price(self):
        """Calculate the unit price based on door specifications."""
        # Get base price from style
        base_price = self.style.price
        
        # Determine woodstock price based on panel type
        if self.style.panel_type.use_flat_panel_price:
            woodstock_price = self.wood_stock.flat_panel_price
        else:
            woodstock_price = self.wood_stock.raised_panel_price
            
        # Calculate and return price per unit (base_price + twice woodstock price)
        return base_price + (woodstock_price * 2)
    
    def __str__(self):
        return f"Door {self.id} - {self.wood_stock.name} {self.style.name}"

    def save(self, *args, **kwargs):
        # Always set type to 'door'
        self.type = 'door'
        # Call the parent save method to handle price calculations
        super().save(*args, **kwargs)


class RailDefaults(BaseModel):
    """Model for default rail sizes for doors."""
    top = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default top rail size in inches"
    )
    bottom = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default bottom rail size in inches"
    )
    left = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default left rail size in inches"
    )
    right = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default right rail size in inches"
    )
    interior_rail_size = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Default interior rail size in inches"
    )
    
    class Meta:
        verbose_name = "Rail Defaults"
        verbose_name_plural = "Rail Defaults"
    
    def __str__(self):
        return f"Rail Defaults: T:{self.top}, B:{self.bottom}, L:{self.left}, R:{self.right}, I:{self.interior_rail_size}"


class MiscellaneousDoorSettings(BaseModel):
    """Model for miscellaneous door settings and defaults."""
    extra_height = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Extra height to add when gluing sheet"
    )
    extra_width = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Extra width to add when gluing sheet"
    )
    glue_min_width = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Minimum width for gluing sheet"
    )
    rail_extra = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Rail joint extra"
    )
    drawer_front = models.ForeignKey(
        PanelType,
        on_delete=models.PROTECT,
        related_name='drawer_front_settings',
        help_text="Panel type to use for drawer fronts"
    )
    drawer_slab = models.ForeignKey(
        PanelType,
        on_delete=models.PROTECT,
        related_name='drawer_slab_settings',
        help_text="Panel type to use for drawer slabs"
    )

    class Meta:
        verbose_name = "Miscellaneous Door Settings"
        verbose_name_plural = "Miscellaneous Door Settings"

    def __str__(self):
        return f"Door Settings (Extra H:{self.extra_height}, W:{self.extra_width})"