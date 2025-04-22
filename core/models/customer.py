from django.db import models
from .base import BaseModel
from ..utils import get_us_states
from django.core.validators import RegexValidator

class Customer(BaseModel):
    company_name = models.CharField(
        max_length=255,
        verbose_name="Company Name"
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name="First Name"
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name="Last Name"
    )
    address_line1 = models.CharField(
        max_length=255,
        verbose_name="Address Line 1"
    )
    address_line2 = models.CharField(
        max_length=255,
        verbose_name="Address Line 2",
        blank=True
    )
    city = models.CharField(
        max_length=255,
        verbose_name="City"
    )
    state = models.CharField(
        max_length=2,
        choices=get_us_states(),
        verbose_name="State"
    )
    zip_code = models.CharField(
        max_length=5,
        validators=[RegexValidator(r'^[0-9]{5}$', 'Enter a valid 5-digit ZIP code')],
        verbose_name="ZIP Code"
    )
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^[0-9]{10}$', 'Enter a valid 10-digit phone number')],
        verbose_name="Phone Number"
    )
    fax = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^[0-9]{10}$', 'Enter a valid 10-digit fax number')],
        verbose_name="Fax Number"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    
    # Add JSON fields for door and drawer defaults
    door_defaults = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Door default preferences for this customer"
    )
    
    drawer_defaults = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Drawer default preferences for this customer"
    )

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.company_name.title()} - {self.first_name.capitalize()} {self.last_name.capitalize()}"

    @property
    def quotes(self):
        """Return only quotes for this customer"""
        return self.orders.filter(is_quote=True)

    @property
    def confirmed_orders(self):
        """Return only confirmed orders for this customer"""
        return self.orders.filter(is_quote=False)

    def save(self, *args, **kwargs):
        # Convert names to lowercase
        self.company_name = self.company_name.lower()
        self.first_name = self.first_name.lower()
        self.last_name = self.last_name.lower()
        self.city = self.city.lower()
        self.address_line1 = self.address_line1.lower()
        self.address_line2 = self.address_line2.lower()
        self.notes = self.notes.lower()

        # Strip any formatting from phone/fax
        if not self.phone.isdigit():
            self.phone = ''.join(filter(str.isdigit, self.phone))
        if not self.fax.isdigit():
            self.fax = ''.join(filter(str.isdigit, self.fax))
        super().save(*args, **kwargs)
    
    def get_door_defaults(self):
        """
        Get door defaults for this customer.
        Returns only customer-specific defaults from the JSON field.
        Does not include global defaults - these should be applied by the view/service
        that uses these values.
        """
        # Simply return the customer defaults as is - no filtering or additions
        return self.door_defaults.copy() if self.door_defaults else {}
    
    def get_drawer_defaults(self):
        """
        Get drawer defaults for this customer.
        Returns customer-specific defaults from the JSON field if present,
        otherwise returns global defaults.
        """
        if self.drawer_defaults:
            return self.drawer_defaults
        else:
            # No need to fallback as the drawer global settings are used by the view
            # and not directly comparable to our JSON structure
            return {}
            
    def set_door_defaults(self, **kwargs):
        """
        Set door defaults for this customer.
        Accepts keyword arguments for door properties.
        If a value is None, it will remove that key from door_defaults.
        """
        # Convert model instances to IDs for JSON serialization
        for key, value in list(kwargs.items()):
            if value is None:
                # Remove this key from door_defaults
                if key in self.door_defaults:
                    self.door_defaults.pop(key)
                # Remove from kwargs to avoid storing None values
                kwargs.pop(key)
            elif hasattr(value, 'pk'):
                kwargs[key] = value.pk
                
        # Update the door_defaults field with remaining values
        if not self.door_defaults:
            self.door_defaults = {}
            
        self.door_defaults.update(kwargs)
        self.save(update_fields=['door_defaults'])
        
    def set_drawer_defaults(self, **kwargs):
        """
        Set drawer defaults for this customer.
        Accepts keyword arguments for drawer properties.
        """
        # Convert model instances to IDs for JSON serialization
        for key, value in kwargs.items():
            if hasattr(value, 'pk'):
                kwargs[key] = value.pk
                
        # Update the drawer_defaults field
        if not self.drawer_defaults:
            self.drawer_defaults = {}
            
        self.drawer_defaults.update(kwargs)
        self.save(update_fields=['drawer_defaults'])

class CustomerDefaults(BaseModel):
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='defaults'
    )
    discount_type = models.CharField(
        max_length=10,
        choices=[
            ('PERCENT', 'Percentage'),
            ('FIXED', 'Fixed Amount')
        ],
        default='PERCENT',
        verbose_name="Discount Type"
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Discount Value"
    )
    surcharge_type = models.CharField(
        max_length=10,
        choices=[
            ('PERCENT', 'Percentage'),
            ('FIXED', 'Fixed Amount')
        ],
        default='PERCENT',
        verbose_name="Surcharge Type"
    )
    surcharge_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Surcharge Value"
    )
    shipping_type = models.CharField(
        max_length=10,
        choices=[
            ('PERCENT', 'Percentage'),
            ('FIXED', 'Fixed Amount')
        ],
        default='PERCENT',
        verbose_name="Shipping Type"
    )
    shipping_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Shipping Value"
    )

    class Meta:
        verbose_name = "Customer Default"
        verbose_name_plural = "Customer Defaults"

    def __str__(self):
        return f"Defaults for {self.customer}"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate percentage values are between 0 and 100
        if self.discount_type == 'PERCENT' and self.discount_value > 100:
            raise ValidationError("Percentage discount cannot exceed 100%")
        if self.surcharge_type == 'PERCENT' and self.surcharge_value > 100:
            raise ValidationError("Percentage surcharge cannot exceed 100%")
        if self.shipping_type == 'PERCENT' and self.shipping_value > 100:
            raise ValidationError("Percentage shipping charge cannot exceed 100%")

    def get_formatted_discount(self):
        """Return formatted string of discount"""
        if self.discount_type == 'PERCENT':
            return f"{self.discount_value}%"
        return f"${self.discount_value}"

    def get_formatted_surcharge(self):
        """Return formatted string of surcharge"""
        if self.surcharge_type == 'PERCENT':
            return f"{self.surcharge_value}%"
        return f"${self.surcharge_value}"

    def get_formatted_shipping(self):
        """Return formatted string of shipping"""
        if self.shipping_type == 'PERCENT':
            return f"{self.shipping_value}%"
        return f"${self.shipping_value}" 