from django import forms
from django.core.validators import MinValueValidator
from decimal import Decimal

class GenericItemForm(forms.Form):
    """Form for adding generic items to an order"""
    
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Item Name",
        help_text="Provide a clear name/description for this item"
    )
    
    price_per_unit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="Price per Unit",
        help_text="Enter the price per individual item"
    )
    
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Quantity",
        help_text="Number of items"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Add any additional validation here if needed
        
        return cleaned_data 