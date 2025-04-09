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
    
    class Meta:
        verbose_name = "Door Item"
        verbose_name_plural = "Door Items"
    
    @property
    def square_feet(self):
        """Calculate the square footage of the door."""
        return (self.width * self.height) / 144  # Convert to square feet
    
    def __str__(self):
        return f"Door {self.id} - {self.wood_stock.name} {self.style.description}" 