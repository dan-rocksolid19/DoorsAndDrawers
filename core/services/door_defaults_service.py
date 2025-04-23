from decimal import Decimal, InvalidOperation
from typing import Dict, Any, Optional, Union
from django.core.exceptions import ObjectDoesNotExist

from ..models.door import WoodStock, EdgeProfile, PanelRise, Style, RailDefaults
from ..models.customer import Customer

class DoorDefaultsService:
    """Service class to handle all door defaults logic."""
    
    RAIL_FIELDS = ['rail_top', 'rail_bottom', 'rail_left', 'rail_right', 'interior_rail_size']
    MODEL_FIELDS = {
        'wood_stock': WoodStock,
        'edge_profile': EdgeProfile,
        'panel_rise': PanelRise,
        'style': Style,
    }
    BOOLEAN_FIELDS = ['sand_edge', 'sand_cross_grain']

    def __init__(self):
        self.global_defaults = self._get_global_defaults()

    def _get_global_defaults(self) -> Dict[str, Decimal]:
        """Get global rail defaults."""
        defaults = RailDefaults.objects.first()
        if not defaults:
            return {
                'rail_top': Decimal('2.500'),
                'rail_bottom': Decimal('2.500'),
                'rail_left': Decimal('2.500'),
                'rail_right': Decimal('2.500'),
                'interior_rail_size': Decimal('1.000')
            }
        return {
            'rail_top': defaults.top,
            'rail_bottom': defaults.bottom,
            'rail_left': defaults.left,
            'rail_right': defaults.right,
            'interior_rail_size': defaults.interior_rail_size
        }

    def get_defaults(self, customer: Customer) -> Dict[str, Any]:
        """
        Get all door defaults for a customer, including resolved model instances.
        Returns a dictionary with both model instances and rail dimensions.
        """
        if not customer.door_defaults:
            return {}

        defaults = {}
        
        # Handle model fields (wood_stock, edge_profile, etc.)
        for field, model_class in self.MODEL_FIELDS.items():
            if field in customer.door_defaults:
                try:
                    instance = model_class.objects.get(pk=customer.door_defaults[field])
                    defaults[field] = instance
                except ObjectDoesNotExist:
                    continue

        # Handle rail dimensions
        for field in self.RAIL_FIELDS:
            if field in customer.door_defaults:
                try:
                    value = Decimal(str(customer.door_defaults[field]))
                    defaults[field] = value
                except (InvalidOperation, TypeError):
                    defaults[field] = self.global_defaults[field]
            else:
                defaults[field] = self.global_defaults[field]

        # Handle boolean fields
        for field in self.BOOLEAN_FIELDS:
            if field in customer.door_defaults:
                defaults[field] = customer.door_defaults[field]

        return defaults

    def get_rail_size(self, customer: Customer, rail_name: str) -> Decimal:
        """Get a specific rail size, falling back to global default if not set."""
        if not customer.door_defaults or rail_name not in customer.door_defaults:
            return self.global_defaults[rail_name]
        
        try:
            return Decimal(str(customer.door_defaults[rail_name]))
        except (InvalidOperation, TypeError):
            return self.global_defaults[rail_name]

    def prepare_defaults_for_storage(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert form data to format suitable for JSONField storage.
        Handles model instances, decimal values, and boolean fields.
        """
        storage_data = {}

        # Handle model instances
        for field, model_class in self.MODEL_FIELDS.items():
            value = form_data.get(field)
            if value is not None:
                if hasattr(value, 'pk'):
                    storage_data[field] = value.pk
                elif value:  # If it's a raw ID
                    storage_data[field] = value

        # Handle rail dimensions
        for field in self.RAIL_FIELDS:
            value = form_data.get(field)
            if value is not None:
                try:
                    decimal_value = Decimal(str(value))
                    # Only store if different from global default
                    if decimal_value != self.global_defaults.get(field):
                        storage_data[field] = str(decimal_value)
                except (InvalidOperation, TypeError):
                    continue

        # Handle boolean fields - only store if True
        for field in self.BOOLEAN_FIELDS:
            value = form_data.get(field)
            if value is True:  # Only store True values
                storage_data[field] = True

        return storage_data

    def apply_defaults_to_form(self, customer: Customer) -> Dict[str, Any]:
        """Prepare defaults for form initial data."""
        return self.get_defaults(customer)

    def apply_defaults_to_line_item(self, line_item: Any, customer: Customer) -> None:
        """Apply defaults to a door line item."""
        defaults = self.get_defaults(customer)
        
        # Apply model defaults
        for field in self.MODEL_FIELDS:
            if field in defaults and getattr(line_item, field, None) is None:
                setattr(line_item, f"{field}_id", defaults[field].pk)

        # Apply rail defaults
        for field in self.RAIL_FIELDS:
            if getattr(line_item, field, None) is None:
                setattr(line_item, field, defaults[field])

        # Apply boolean defaults
        for field in self.BOOLEAN_FIELDS:
            if field in defaults and getattr(line_item, field, None) is None:
                setattr(line_item, field, defaults[field]) 