from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..models.door import WoodStock, Design, PanelType, EdgeProfile, PanelRise, Style
from ..forms import GenericItemForm

def settings(request):
    """
    View to render the main settings page.
    """
    return render(request, 'settings/settings.html', {
        'title': 'Settings'
    })

def door_settings(request):
    """
    View to render the door settings page with WoodStock, Design, PanelType, EdgeProfile, PanelRise and Style data.
    """
    # Retrieve all WoodStock entries
    wood_stocks = WoodStock.objects.all().order_by('name')
    
    # Retrieve all Design entries
    designs = Design.objects.all().order_by('name')
    
    # Retrieve all PanelType entries
    panel_types = PanelType.objects.all().order_by('name')
    
    # Retrieve all EdgeProfile entries
    edge_profiles = EdgeProfile.objects.all().order_by('name')
    
    # Retrieve all PanelRise entries
    panel_rises = PanelRise.objects.all().order_by('name')
    
    # Retrieve all Style entries
    styles = Style.objects.all().order_by('name')
    
    return render(request, 'settings/door_settings.html', {
        'title': 'Door Settings',
        'wood_stocks': wood_stocks,
        'designs': designs,
        'panel_types': panel_types,
        'edge_profiles': edge_profiles,
        'panel_rises': panel_rises,
        'styles': styles
    })

def drawer_settings(request):
    """
    View to render the drawer settings page.
    """
    return render(request, 'settings/drawer_settings.html', {
        'title': 'Drawer Settings'
    })

def generic_item_form(request):
    """
    View to render the generic item form for adding miscellaneous items to an order.
    """
    form = GenericItemForm()
    return render(request, 'order/partials/generic_form.html', {
        'form': form
    })

@require_http_methods(["POST"])
def add_generic_item(request):
    """
    View to handle adding a generic/miscellaneous item.
    Receives payload with item specifications and adds to session-based order.
    """
    try:
        if not request.session.get("current_order"):
            return JsonResponse({"error": "Select a customer."}, status=401)
        
        # Use the GenericItemForm for validation
        form = GenericItemForm(request.POST)
        
        if not form.is_valid():
            # Return form errors
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({'error': 'Form validation failed', 'field_errors': errors}, status=400)
            
        # Get cleaned data from the form
        cleaned_data = form.cleaned_data
        
        # Extract item specifications from cleaned data
        name = cleaned_data['name']
        quantity = cleaned_data['quantity']
        price_per_unit = cleaned_data['price_per_unit']
        
        # Calculate total price
        total_price = price_per_unit * quantity
        
        # Create generic item
        generic_item = {
            'type': 'other',
            'name': name,
            'quantity': str(quantity),
            'price_per_unit': str(price_per_unit),
            'total_price': str(total_price)
        }
        
        # Add the item to the session order
        request.session['current_order']['items'].append(generic_item)
        # Mark session as modified
        request.session.modified = True
        
        return render(request, 'door/line_items_table.html', {
            'items': request.session['current_order']['items']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
