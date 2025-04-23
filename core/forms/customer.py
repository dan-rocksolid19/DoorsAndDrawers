from django import forms
from ..models.customer import Customer, CustomerDefaults
from ..models.door import WoodStock, EdgeProfile, PanelRise, Style
from ..models.drawer import DrawerWoodStock, DrawerEdgeType, DrawerBottomSize

class PhoneNumberWidget(forms.TextInput):
    def value_from_datadict(self, data, files, name):
        """Strip formatting before saving"""
        value = super().value_from_datadict(data, files, name)
        return ''.join(filter(str.isdigit, value))

class CustomerForm(forms.ModelForm):
    # Defaults fields
    discount_type = forms.ChoiceField(
        choices=[
            ('PERCENT', 'Percentage'),
            ('FIXED', 'Fixed Amount')
        ],
        initial='PERCENT',
        required=False
    )
    discount_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        required=False
    )
    surcharge_type = forms.ChoiceField(
        choices=[
            ('PERCENT', 'Percentage'),
            ('FIXED', 'Fixed Amount')
        ],
        initial='PERCENT',
        required=False
    )
    surcharge_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        required=False
    )
    shipping_type = forms.ChoiceField(
        choices=[
            ('PERCENT', 'Percentage'),
            ('FIXED', 'Fixed Amount')
        ],
        initial='PERCENT',
        required=False
    )
    shipping_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        required=False
    )

    class Meta:
        model = Customer
        fields = [
            'company_name',
            'first_name',
            'last_name',
            'address_line1',
            'address_line2',
            'state',
            'city',
            'zip_code',
            'phone',
            'fax',
            'notes',
            'taxable'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit, building, floor, etc.'}),
            'phone': PhoneNumberWidget(),
            'fax': PhoneNumberWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                defaults = self.instance.defaults
                self.fields['discount_type'].initial = defaults.discount_type
                self.fields['discount_value'].initial = defaults.discount_value
                self.fields['surcharge_type'].initial = defaults.surcharge_type
                self.fields['surcharge_value'].initial = defaults.surcharge_value
                self.fields['shipping_type'].initial = defaults.shipping_type
                self.fields['shipping_value'].initial = defaults.shipping_value
            except CustomerDefaults.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        # Convert names to lowercase
        cleaned_data['company_name'] = cleaned_data.get('company_name', '').lower()
        cleaned_data['first_name'] = cleaned_data.get('first_name', '').lower()
        cleaned_data['last_name'] = cleaned_data.get('last_name', '').lower()

        # Validate percentage values
        if cleaned_data.get('discount_type') == 'PERCENT' and cleaned_data.get('discount_value', 0) > 100:
            self.add_error('discount_value', 'Percentage discount cannot exceed 100%')
        if cleaned_data.get('surcharge_type') == 'PERCENT' and cleaned_data.get('surcharge_value', 0) > 100:
            self.add_error('surcharge_value', 'Percentage surcharge cannot exceed 100%')
        if cleaned_data.get('shipping_type') == 'PERCENT' and cleaned_data.get('shipping_value', 0) > 100:
            self.add_error('shipping_value', 'Percentage shipping charge cannot exceed 100%')

        return cleaned_data

    def save(self, commit=True):
        customer = super().save(commit=commit)
        if commit:
            # Create or update defaults
            defaults, created = CustomerDefaults.objects.get_or_create(
                customer=customer,
                defaults={
                    'discount_type': self.cleaned_data['discount_type'],
                    'discount_value': self.cleaned_data['discount_value'],
                    'surcharge_type': self.cleaned_data['surcharge_type'],
                    'surcharge_value': self.cleaned_data['surcharge_value'],
                    'shipping_type': self.cleaned_data['shipping_type'],
                    'shipping_value': self.cleaned_data['shipping_value'],
                }
            )
            if not created:
                defaults.discount_type = self.cleaned_data['discount_type']
                defaults.discount_value = self.cleaned_data['discount_value']
                defaults.surcharge_type = self.cleaned_data['surcharge_type']
                defaults.surcharge_value = self.cleaned_data['surcharge_value']
                defaults.shipping_type = self.cleaned_data['shipping_type']
                defaults.shipping_value = self.cleaned_data['shipping_value']
                defaults.save()
        return customer

class CustomerDoorDefaultsForm(forms.Form):
    """Form for managing customer door defaults"""
    wood_stock = forms.ModelChoiceField(
        queryset=WoodStock.objects.all(),
        required=False,
        label="Default Wood Stock"
    )
    edge_profile = forms.ModelChoiceField(
        queryset=EdgeProfile.objects.all(),
        required=False,
        label="Default Edge Profile"
    )
    panel_rise = forms.ModelChoiceField(
        queryset=PanelRise.objects.all(),
        required=False,
        label="Default Panel Rise"
    )
    style = forms.ModelChoiceField(
        queryset=Style.objects.all(),
        required=False,
        label="Default Style"
    )
    rail_top = forms.DecimalField(
        max_digits=5,
        decimal_places=3,
        required=False,
        label="Default Top Rail Size (inches)"
    )
    rail_bottom = forms.DecimalField(
        max_digits=5,
        decimal_places=3,
        required=False,
        label="Default Bottom Rail Size (inches)"
    )
    rail_left = forms.DecimalField(
        max_digits=5,
        decimal_places=3,
        required=False,
        label="Default Left Rail Size (inches)"
    )
    rail_right = forms.DecimalField(
        max_digits=5,
        decimal_places=3,
        required=False,
        label="Default Right Rail Size (inches)"
    )
    interior_rail_size = forms.DecimalField(
        max_digits=5,
        decimal_places=3,
        required=False,
        label="Default Interior Rail Size (inches)"
    )
    sand_edge = forms.BooleanField(
        required=False,
        label="Sand Edge by Default"
    )
    sand_cross_grain = forms.BooleanField(
        required=False,
        label="Sand Cross Grain by Default"
    )


class CustomerDrawerDefaultsForm(forms.Form):
    """Form for managing customer drawer defaults"""
    wood_stock = forms.ModelChoiceField(
        queryset=DrawerWoodStock.objects.all(),
        required=False,
        label="Default Wood Stock"
    )
    edge_type = forms.ModelChoiceField(
        queryset=DrawerEdgeType.objects.all(),
        required=False,
        label="Default Edge Type"
    )
    bottom = forms.ModelChoiceField(
        queryset=DrawerBottomSize.objects.all(),
        required=False,
        label="Default Bottom Size"
    )
    undermount = forms.BooleanField(
        required=False,
        label="Use Undermount Slides by Default"
    )
    finishing = forms.BooleanField(
        required=False,
        label="Apply Finishing by Default"
    ) 