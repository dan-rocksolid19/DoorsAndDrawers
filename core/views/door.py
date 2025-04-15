from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from ..forms import DoorForm
from ..models.door import WoodStock, EdgeProfile, PanelRise, Style, RailDefaults
from decimal import Decimal

@require_http_methods(["GET", "POST"])
def door_form(request):
    """
    View to handle the door form.
    GET: Returns the form template
    POST: Processes the form data
    """
    form = DoorForm()
    
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

@require_http_methods(["POST"])
def add_door(request):
    """
    View to handle adding a door.
    Receives payload with door specifications and adds to session-based order.
    """
    try:
        if not request.session.get("current_order"):
            return JsonResponse({"error": "Select a customer."}, status=401)
        
        # Use the DoorForm for validation
        form = DoorForm(request.POST)
        
        if not form.is_valid():
            # Return form errors
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({'error': 'Form validation failed', 'field_errors': errors}, status=400)
            
        # Get cleaned data from the form
        cleaned_data = form.cleaned_data
        
        # Extract door specifications from cleaned data
        wood_stock = cleaned_data['wood_stock']
        edge_profile = cleaned_data['edge_profile']
        panel_rise = cleaned_data['panel_rise']
        style = cleaned_data['style']
        width = cleaned_data['width']
        height = cleaned_data['height']
        quantity = cleaned_data['quantity']
        
        # Extract rail dimensions
        rail_top = cleaned_data['rail_top']
        rail_bottom = cleaned_data['rail_bottom']
        rail_left = cleaned_data['rail_left']
        rail_right = cleaned_data['rail_right']
            
        # Calculate price using the same logic as in create_order
        base_price = style.price
        
        # Determine woodstock price based on panel type
        if style.panel_type.use_flat_panel_price:
            woodstock_price = wood_stock.flat_panel_price
        else:
            woodstock_price = wood_stock.raised_panel_price
            
        # Calculate price per unit (base_price + twice woodstock price)
        price_per_unit = base_price + (woodstock_price * 2)
        
        # Calculate total price (price_per_unit * quantity)
        total_price = price_per_unit * quantity
        
        # Create door item
        door_item = {
            'type': 'door',
            'wood_stock': {'id': wood_stock.pk, 'name': wood_stock.name},
            'edge_profile': {'id': edge_profile.pk, 'name': edge_profile.name},
            'panel_rise': {'id': panel_rise.pk, 'name': panel_rise.name},
            'style': {'id': style.pk, 'name': style.name},
            'width': str(width),
            'height': str(height),
            'quantity': str(quantity),
            'price_per_unit': str(price_per_unit),
            'total_price': str(total_price),
            'rail_top': str(rail_top),
            'rail_bottom': str(rail_bottom),
            'rail_left': str(rail_left),
            'rail_right': str(rail_right)
        }
        
        # Add the door to the session order
        request.session['current_order']['items'].append(door_item)
        # Mark session as modified
        request.session.modified = True
        
        return render(request, 'door/line_items_table.html', {
            'items': request.session['current_order']['items']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)