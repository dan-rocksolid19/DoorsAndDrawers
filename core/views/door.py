from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from ..forms import DoorForm
from ..models.door import WoodStock, EdgeProfile, PanelRise, Style, RailDefaults, DoorLineItem
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
        
        # Extract custom price information from POST data (not part of the form model)
        custom_price = request.POST.get('custom_price') == 'on'
        price_per_unit_manual = request.POST.get('price_per_unit_manual')
        
        # Create a DoorLineItem instance without saving it to the database
        door_item_model = DoorLineItem(**cleaned_data)
        
        # Apply custom price if provided
        if custom_price and price_per_unit_manual:
            try:
                door_item_model.custom_price = True
                door_item_model.price_per_unit = Decimal(price_per_unit_manual)
            except (ValueError, TypeError):
                # If price_per_unit_manual is not a valid decimal, use calculated price instead
                door_item_model.custom_price = False
        else:
            door_item_model.custom_price = False
            door_item_model.price_per_unit = door_item_model.calculate_price()
        
        # Get the calculated price from the model
        price = door_item_model.price
        
        # Create door item dictionary for session storage
        door_item = {
            'type': 'door',
            'wood_stock': {'id': cleaned_data['wood_stock'].pk, 'name': cleaned_data['wood_stock'].name},
            'edge_profile': {'id': cleaned_data['edge_profile'].pk, 'name': cleaned_data['edge_profile'].name},
            'panel_rise': {'id': cleaned_data['panel_rise'].pk, 'name': cleaned_data['panel_rise'].name},
            'style': {'id': cleaned_data['style'].pk, 'name': cleaned_data['style'].name},
            'width': str(cleaned_data['width']),
            'height': str(cleaned_data['height']),
            'quantity': str(cleaned_data['quantity']),
            'price_per_unit': str(door_item_model.price_per_unit),
            'total_price': str(price),
            'rail_top': str(cleaned_data['rail_top']),
            'rail_bottom': str(cleaned_data['rail_bottom']),
            'rail_left': str(cleaned_data['rail_left']),
            'rail_right': str(cleaned_data['rail_right']),
            'custom_price': custom_price
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