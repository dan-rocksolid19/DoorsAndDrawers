from django import forms
from ..models import Order
from django.utils import timezone

class BaseOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Only set default if this is a new instance
            self.initial['order_date'] = timezone.localdate()

    class Meta:
        model = Order
        fields = [
            'customer',
            'billing_address1',
            'billing_address2',
            'order_date',
        ]
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
        }

class OrderForm(BaseOrderForm):
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_quote = False
        if commit:
            instance.save()
        return instance

class QuoteForm(BaseOrderForm):
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_quote = True
        if commit:
            instance.save()
        return instance 