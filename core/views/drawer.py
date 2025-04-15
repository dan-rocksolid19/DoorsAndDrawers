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
        
        # Extract drawer specifications from cleaned data
        wood_stock = cleaned_data['wood_stock']
        edge_type = cleaned_data['edge_type']
        bottom = cleaned_data['bottom']
        width = cleaned_data['width']
        height = cleaned_data['height']
        depth = cleaned_data['depth']
        quantity = cleaned_data['quantity']
        undermount = cleaned_data['undermount']
        finishing = cleaned_data['finishing']
            
        # Calculate a simple price (this would be replaced with your actual pricing logic)
        base_price = Decimal('10.00')  # Basic drawer price
        # Add woodstock price
        price_per_unit = base_price + wood_stock.price + bottom.price
        
        # Apply additional costs if applicable
        if undermount:
            price_per_unit += Decimal('5.00')  # Extra cost for undermount
        if finishing:
            price_per_unit += Decimal('3.00')  # Extra cost for finishing
        
        # Calculate total price
        total_price = price_per_unit * quantity
        
        # Create drawer item
        drawer_item = {
            'type': 'drawer',
            'wood_stock': {'id': wood_stock.pk, 'name': wood_stock.name},
            'edge_type': {'id': edge_type.pk, 'name': edge_type.name},
            'bottom': {'id': bottom.pk, 'name': bottom.name},
            'width': str(width),
            'height': str(height),
            'depth': str(depth),
            'quantity': str(quantity),
            'undermount': undermount,
            'finishing': finishing,
            'price_per_unit': str(price_per_unit),
            'total_price': str(total_price)
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