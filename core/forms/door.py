from django import forms
from django.forms import ModelForm
from ..models.door import (
    DoorLineItem, WoodStock, EdgeProfile, 
    PanelRise, Style, RailDefaults
)
from decimal import Decimal

class DoorForm(ModelForm):
    """Form for creating and editing door line items."""
    
    # Override the foreign key fields to use ModelChoiceField with proper ordering
    wood_stock = forms.ModelChoiceField(
        queryset=WoodStock.objects.all().order_by('name'),
        empty_label="Select Wood Type"
    )
    
    edge_profile = forms.ModelChoiceField(
        queryset=EdgeProfile.objects.all().order_by('name'),
        empty_label="Select Edge Profile"
    )
    
    panel_rise = forms.ModelChoiceField(
        queryset=PanelRise.objects.all().order_by('name'),
        empty_label="Select Panel Rise"
    )
    
    style = forms.ModelChoiceField(
        queryset=Style.objects.all().order_by('name'),
        empty_label="Select Style"
    )
    
    width = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    height = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    # Rail dimension fields
    rail_top = forms.DecimalField(
        min_value=0.001,
        max_digits=5,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'step': '0.001',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    rail_bottom = forms.DecimalField(
        min_value=0.001,
        max_digits=5,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'step': '0.001',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    rail_left = forms.DecimalField(
        min_value=0.001,
        max_digits=5,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'step': '0.001',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    rail_right = forms.DecimalField(
        min_value=0.001,
        max_digits=5,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'step': '0.001',
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    class Meta:
        model = DoorLineItem
        fields = [
            'wood_stock', 'edge_profile', 'panel_rise', 
            'style', 'width', 'height', 
            'rail_top', 'rail_bottom', 'rail_left', 'rail_right',
            'quantity'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get rail defaults
        rail_defaults = RailDefaults.objects.first()
        
        # Set initial values for rail dimensions from defaults
        if rail_defaults:
            self.fields['rail_top'].initial = rail_defaults.top
            self.fields['rail_bottom'].initial = rail_defaults.bottom
            self.fields['rail_left'].initial = rail_defaults.left
            self.fields['rail_right'].initial = rail_defaults.right
        else:
            # Use fallback values if no defaults exist
            self.fields['rail_top'].initial = Decimal('2.50')
            self.fields['rail_bottom'].initial = Decimal('2.50')
            self.fields['rail_left'].initial = Decimal('2.50')
            self.fields['rail_right'].initial = Decimal('2.50')
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                if not field.widget.attrs.get('class'):
                    field.widget.attrs['class'] = 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
                    
            # Add help text to dimension fields
            if field_name == 'width':
                field.help_text = "Width in inches"
            elif field_name == 'height':
                field.help_text = "Height in inches"
            elif field_name == 'rail_top':
                field.help_text = "Top rail size in inches"
            elif field_name == 'rail_bottom':
                field.help_text = "Bottom rail size in inches"
            elif field_name == 'rail_left':
                field.help_text = "Left rail size in inches"
            elif field_name == 'rail_right':
                field.help_text = "Right rail size in inches" 