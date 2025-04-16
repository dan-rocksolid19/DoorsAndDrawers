from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from ..models.drawer import DrawerLineItem, DrawerWoodStock, DrawerEdgeType, DrawerBottomSize
from ..forms import DrawerForm
from decimal import Decimal
import json
from django.urls import reverse
from core.models import Order

def drawer_form(request):
    """Render the drawer form partial template."""
    wood_stocks = DrawerWoodStock.objects.all()
    edge_types = DrawerEdgeType.objects.all()
    bottom_sizes = DrawerBottomSize.objects.all()
    
    form = DrawerForm()
    
    context = {
        'form': form,
        'wood_stocks': wood_stocks,
        'edge_types': edge_types,
        'bottom_sizes': bottom_sizes,
    }
    
    return render(request, 'drawer/drawer_form.html', context)

@require_http_methods(["POST"])
def add_drawer(request):
    """
    View to handle adding a drawer.
    Receives payload with drawer specifications and adds to session-based order.
    """
    try:
        if not request.session.get("current_order"):
            return JsonResponse({"error": "Select a customer."}, status=401)
        
        # Use the DrawerForm for validation
        form = DrawerForm(request.POST)
        
        if not form.is_valid():
            # Return form errors
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({'error': 'Form validation failed', 'field_errors': errors}, status=400)
            
        # Get cleaned data from the form
        cleaned_data = form.cleaned_data
        
        # Get custom price information (using the drawer-specific field names)
        custom_price = request.POST.get('custom_price') == 'on'
        price_per_unit_manual = request.POST.get('price_per_unit_manual')
        
        # Create a DrawerLineItem model instance for price calculation
        drawer_item_model=DrawerLineItem(**cleaned_data)

        # Apply custom price if provided
        if custom_price and price_per_unit_manual:
            try:
                drawer_item_model.custom_price = True
                drawer_item_model.price_per_unit = Decimal(price_per_unit_manual)
            except (ValueError, TypeError):
                # If price_per_unit_manual is not a valid decimal, use calculated price
                drawer_item_model.custom_price = False
        else:
            drawer_item_model.custom_price = False
            drawer_item_model.price_per_unit = drawer_item_model.calculate_price()

        # Get the calculated price
        price = drawer_item_model.price
        
        # Create drawer item for session storage
        drawer_item = {
            'type': 'drawer',
            'wood_stock': {'id': cleaned_data['wood_stock'].pk, 'name': cleaned_data['wood_stock'].name},
            'edge_type': {'id': cleaned_data['edge_type'].pk, 'name': cleaned_data['edge_type'].name},
            'bottom': {'id': cleaned_data['bottom'].pk, 'name': cleaned_data['bottom'].name},
            'width': str(cleaned_data['width']),
            'height': str(cleaned_data['height']),
            'depth': str(cleaned_data['depth']),
            'quantity': str(cleaned_data['quantity']),
            'undermount': cleaned_data['undermount'],
            'finishing': cleaned_data['finishing'],
            'price_per_unit': str(drawer_item_model.price_per_unit),
            'total_price': str(price),
            'custom_price': custom_price
        }
        
        # Add the drawer to the session order
        request.session['current_order']['items'].append(drawer_item)
        # Mark session as modified
        request.session.modified = True
        
        return render(request, 'door/line_items_table.html', {
            'items': request.session['current_order']['items']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 