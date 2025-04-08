from django import forms
from django.forms import ModelForm
from ..models.door import (
    DoorLineItem, WoodStock, EdgeProfile, 
    PanelRise, Style
)

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
            'style', 'width', 'height', 'quantity'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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