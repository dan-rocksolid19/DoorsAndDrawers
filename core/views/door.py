from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from ..forms import DoorForm
from ..models.door import DoorLineItem, WoodStock, EdgeProfile, PanelRise, Style
from .common import process_line_item_form
from decimal import Decimal, InvalidOperation

@require_http_methods(["GET", "POST"])
def door_form(request):
    """
    View to handle the door form.
    GET: Returns the form template
    POST: Processes the form data
    """
    # Initial data for the form
    initial_data = {}
    
    # Check if we have a customer in the session
    customer = get_current_customer(request)
    
    # If we have a customer, get their defaults
    if customer:
        door_defaults = customer.get_door_defaults()
        
        # Apply known defaults from JSON
        if 'wood_stock' in door_defaults:
            try:
                initial_data['wood_stock'] = WoodStock.objects.get(pk=door_defaults['wood_stock'])
            except (WoodStock.DoesNotExist, ValueError, TypeError):
                pass
                
        if 'edge_profile' in door_defaults:
            try:
                initial_data['edge_profile'] = EdgeProfile.objects.get(pk=door_defaults['edge_profile'])
            except (EdgeProfile.DoesNotExist, ValueError, TypeError):
                pass
                
        if 'panel_rise' in door_defaults:
            try:
                initial_data['panel_rise'] = PanelRise.objects.get(pk=door_defaults['panel_rise'])
            except (PanelRise.DoesNotExist, ValueError, TypeError):
                pass
                
        if 'style' in door_defaults:
            try:
                initial_data['style'] = Style.objects.get(pk=door_defaults['style'])
            except (Style.DoesNotExist, ValueError, TypeError):
                pass
        
        # Apply rail defaults
        for rail in ['rail_top', 'rail_bottom', 'rail_left', 'rail_right']:
            if rail in door_defaults:
                try:
                    initial_data[rail] = Decimal(door_defaults[rail])
                except (InvalidOperation, TypeError):
                    pass
    
    # Create form with initial data
    form = DoorForm(initial=initial_data)
    
    # If this is a POST request, process the form data
    if request.method == 'POST':
        form = DoorForm(request.POST)
        if form.is_valid():
            # In a real scenario, we might create and save the door
            # door = form.save()
            pass
    
    # Return the form template
    return render(request, 'door/door_form.html', {
        'form': form,
    })

def transform_door_data(cleaned_data, door_model, item_type, custom_price, price):
    """Transform door form data to session format"""
    return {
        'type': item_type,
        'wood_stock': {'id': cleaned_data['wood_stock'].pk, 'name': cleaned_data['wood_stock'].name},
        'edge_profile': {'id': cleaned_data['edge_profile'].pk, 'name': cleaned_data['edge_profile'].name},
        'panel_rise': {'id': cleaned_data['panel_rise'].pk, 'name': cleaned_data['panel_rise'].name},
        'style': {'id': cleaned_data['style'].pk, 'name': cleaned_data['style'].name},
        'width': str(cleaned_data['width']),
        'height': str(cleaned_data['height']),
        'quantity': str(cleaned_data['quantity']),
        'price_per_unit': str(door_model.price_per_unit),
        'total_price': str(price),
        'rail_top': str(cleaned_data['rail_top']),
        'rail_bottom': str(cleaned_data['rail_bottom']),
        'rail_left': str(cleaned_data['rail_left']),
        'rail_right': str(cleaned_data['rail_right']),
        'custom_price': custom_price
    }

@require_http_methods(["POST"])
def add_door(request):
    """
    View to handle adding a door.
    Receives payload with door specifications and adds to session-based order.
    """
    return process_line_item_form(
        request, 
        DoorForm, 
        DoorLineItem, 
        'door',
        transform_door_data
    )

def get_current_customer(request):
    """
    Get the current customer from session or order
    
    Args:
        request: HTTP request object
        
    Returns:
        Customer object or None
    """
    from ..models import Customer
    
    # If we have a current order in the session
    if 'current_order' in request.session:
        # Check for customer key in the current_order
        if 'customer' in request.session['current_order']:
            customer_id = request.session['current_order']['customer']
            try:
                return Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                pass
    
    return None