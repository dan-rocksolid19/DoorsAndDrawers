from django.shortcuts import render
from .customer import (
    customers, customer_detail, new_customer,
    edit_customer, delete_customer
)
from .order import (
    orders, order_detail, create_order,
    delete_order
)
from .quote import (
    quotes, quote_detail, create_quote,
    delete_quote, convert_to_order
)
from .line_item import (
    settings, door_settings, drawer_settings,
    generic_item_form
)
from .door import (
    door_form, add_door
)
from .drawer import (
    drawer_form, add_drawer
)
# Import common utilities
from . import common

def home(request):
    return render(request, 'home.html', {
        'title': 'Home'
    })

__all__ = [
    'home',
    'customers', 'customer_detail', 'new_customer',
    'edit_customer', 'delete_customer',
    'orders', 'order_detail', 'create_order',
    'delete_order',
    'quotes', 'quote_detail', 'create_quote',
    'delete_quote', 'convert_to_order',
    'settings', 'door_settings', 'drawer_settings',
    'door_form', 'drawer_form', 'add_drawer',
    'common'  # Make common module available
] 