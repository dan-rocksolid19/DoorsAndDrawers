from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from ..models.drawer import DrawerLineItem, DrawerWoodStock, DrawerEdgeType, DrawerBottomSize
from ..forms import DrawerForm
from .common import process_line_item_form
from .door import get_current_customer

def drawer_form(request):
    """Render the drawer form partial template."""
    wood_stocks = DrawerWoodStock.objects.all()
    edge_types = DrawerEdgeType.objects.all()
    bottom_sizes = DrawerBottomSize.objects.all()
    
    # Initial data for the form
    initial_data = {}
    
    # Check if we have a customer in the session
    customer = get_current_customer(request)
    
    # If we have a customer, get their defaults
    if customer:
        drawer_defaults = customer.get_drawer_defaults()
        
        # Apply known defaults from JSON
        if 'wood_stock' in drawer_defaults:
            try:
                initial_data['wood_stock'] = DrawerWoodStock.objects.get(pk=drawer_defaults['wood_stock'])
            except (DrawerWoodStock.DoesNotExist, ValueError, TypeError):
                pass
                
        if 'edge_type' in drawer_defaults:
            try:
                initial_data['edge_type'] = DrawerEdgeType.objects.get(pk=drawer_defaults['edge_type'])
            except (DrawerEdgeType.DoesNotExist, ValueError, TypeError):
                pass
                
        if 'bottom' in drawer_defaults:
            try:
                initial_data['bottom'] = DrawerBottomSize.objects.get(pk=drawer_defaults['bottom'])
            except (DrawerBottomSize.DoesNotExist, ValueError, TypeError):
                pass
        
        # Apply boolean options
        for option in ['undermount', 'finishing']:
            if option in drawer_defaults:
                initial_data[option] = drawer_defaults[option]
    
    # Create form with initial data
    form = DrawerForm(initial=initial_data)
    
    context = {
        'form': form,
        'wood_stocks': wood_stocks,
        'edge_types': edge_types,
        'bottom_sizes': bottom_sizes,
    }
    
    return render(request, 'drawer/drawer_form.html', context)

def transform_drawer_data(cleaned_data, drawer_model, item_type, custom_price, price):
    """Transform drawer form data to session format"""
    return {
        'type': item_type,
        'wood_stock': {'id': cleaned_data['wood_stock'].pk, 'name': cleaned_data['wood_stock'].name},
        'edge_type': {'id': cleaned_data['edge_type'].pk, 'name': cleaned_data['edge_type'].name},
        'bottom': {'id': cleaned_data['bottom'].pk, 'name': cleaned_data['bottom'].name},
        'width': str(cleaned_data['width']),
        'height': str(cleaned_data['height']),
        'depth': str(cleaned_data['depth']),
        'quantity': str(cleaned_data['quantity']),
        'undermount': cleaned_data['undermount'],
        'finishing': cleaned_data['finishing'],
        'price_per_unit': str(drawer_model.price_per_unit),
        'total_price': str(price),
        'custom_price': custom_price
    }

@require_http_methods(["POST"])
def add_drawer(request):
    """
    View to handle adding a drawer.
    Receives payload with drawer specifications and adds to session-based order.
    """
    return process_line_item_form(
        request, 
        DrawerForm, 
        DrawerLineItem, 
        'drawer',
        transform_drawer_data
    ) 