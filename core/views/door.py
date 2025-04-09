from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from ..forms import DoorForm
from ..models.door import WoodStock, EdgeProfile, PanelRise, Style
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

        if not request.session["current_order"]:
            return JsonResponse({"error": "Select a customer."}, status=401)
        # Access POST data directly
        data = request.POST
        
        # Extract door specifications
        wood_stock_id = data.get('wood_stock')
        edge_profile_id = data.get('edge_profile')
        panel_rise_id = data.get('panel_rise')
        style_id = data.get('style')
        width = data.get('width')
        height = data.get('height')
        quantity = data.get('quantity', '1')
        
        # Ensure required values are present
        if not all([wood_stock_id, edge_profile_id, panel_rise_id, style_id, width, height]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Validate numeric fields
        try:
            width = Decimal(str(width).replace(',', '.'))
            height = Decimal(str(height).replace(',', '.'))
            quantity = int(quantity)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid numeric values'}, status=400)
        
        # Get models from database for validation (would add error handling in production)
        try:
            wood_stock = WoodStock.objects.get(id=wood_stock_id)
            edge_profile = EdgeProfile.objects.get(id=edge_profile_id)
            panel_rise = PanelRise.objects.get(id=panel_rise_id)  
            style = Style.objects.get(id=style_id)
        except Exception as e:
            return JsonResponse({'error': f'Invalid reference data: {str(e)}'}, status=400)
            
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
            'total_price': str(total_price)
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