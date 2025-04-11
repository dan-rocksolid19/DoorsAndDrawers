from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import Style, PanelType, Design, WoodStock, EdgeProfile, PanelRise, RailDefaults

def door_settings(request):
    """
    Render the door settings page with all door components
    """
    styles = Style.objects.all().select_related('panel_type', 'design')
    wood_stocks = WoodStock.objects.all()
    designs = Design.objects.all()
    edge_profiles = EdgeProfile.objects.all()
    panel_rises = PanelRise.objects.all()
    panel_types = PanelType.objects.all()
    rail_defaults = RailDefaults.objects.first()  # Get the first (should be only one) rail defaults
    
    context = {
        'styles': styles,
        'wood_stocks': wood_stocks,
        'designs': designs,
        'edge_profiles': edge_profiles,
        'panel_rises': panel_rises,
        'panel_types': panel_types,
        'rail_defaults': rail_defaults,
        'title': 'Door Settings'
    }
    
    return render(request, 'settings/door_settings.html', context)

# Door Style editing views
def edit_door_style(request, style_id):
    """
    Switch a door style row to edit mode
    """
    style = get_object_or_404(Style, id=style_id)
    panel_types = PanelType.objects.all()
    designs = Design.objects.all()
    
    context = {
        'style': style,
        'panel_types': panel_types,
        'designs': designs,
    }
    
    return render(request, 'settings/partials/style_row_edit.html', context)

def get_door_style(request, style_id):
    """
    Return a door style row in display mode (for cancel button)
    """
    style = get_object_or_404(Style, id=style_id)
    
    return render(request, 'settings/partials/style_row_display.html', {'style': style})

def update_door_style(request, style_id):
    """
    Process the form submission and update the door style
    """
    style = get_object_or_404(Style, id=style_id)
    
    if request.method == 'POST':
        # Update the style with form data
        style.name = request.POST.get('name')
        style.panel_type_id = request.POST.get('panel_type')
        style.design_id = request.POST.get('design')
        
        # Handle numeric values with validation
        try:
            style.price = Decimal(request.POST.get('price', '0'))
            style.panels_across = int(request.POST.get('panels_across', '1'))
            style.panels_down = int(request.POST.get('panels_down', '1'))
            style.panel_overlap = Decimal(request.POST.get('panel_overlap', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/style_row_edit.html', {
                'style': style,
                'panel_types': PanelType.objects.all(),
                'designs': Design.objects.all(),
                'errors': {'price': ['Please enter valid numbers for all numeric fields']}
            }, status=422)
        
        style.designs_on_top = 'designs_on_top' in request.POST
        style.designs_on_bottom = 'designs_on_bottom' in request.POST
        
        try:
            style.full_clean()  # Validate the model
            style.save()
        except ValidationError as e:
            # Return the edit form with error messages
            context = {
                'style': style,
                'panel_types': PanelType.objects.all(),
                'designs': Design.objects.all(),
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/style_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/style_row_display.html', {'style': style})
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

# Wood Stock editing views
def edit_wood_stock(request, stock_id):
    """
    Switch a wood stock row to edit mode
    """
    wood = get_object_or_404(WoodStock, id=stock_id)
    
    context = {
        'wood': wood,
    }
    
    return render(request, 'settings/partials/wood_stock_row_edit.html', context)

def get_wood_stock(request, stock_id):
    """
    Return a wood stock row in display mode (for cancel button)
    """
    wood = get_object_or_404(WoodStock, id=stock_id)
    
    return render(request, 'settings/partials/wood_stock_row_display.html', {'wood': wood})

def update_wood_stock(request, stock_id):
    """
    Process the form submission and update the wood stock
    """
    wood = get_object_or_404(WoodStock, id=stock_id)
    
    if request.method == 'POST':
        # Update the wood stock with form data
        wood.name = request.POST.get('name')
        
        # Handle numeric values with validation
        try:
            wood.raised_panel_price = Decimal(request.POST.get('raised_panel_price', '0'))
            wood.flat_panel_price = Decimal(request.POST.get('flat_panel_price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/wood_stock_row_edit.html', {
                'wood': wood,
                'errors': {'raised_panel_price': ['Please enter valid numbers for price fields']}
            }, status=422)
        
        try:
            wood.full_clean()  # Validate the model
            wood.save()
        except ValidationError as e:
            # Return the edit form with error messages
            context = {
                'wood': wood,
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/wood_stock_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/wood_stock_row_display.html', {'wood': wood})
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

# Door Design editing views
def edit_door_design(request, design_id):
    """
    Switch a door design row to edit mode
    """
    design = get_object_or_404(Design, id=design_id)
    
    context = {
        'design': design,
    }
    
    return render(request, 'settings/partials/design_row_edit.html', context)

def get_door_design(request, design_id):
    """
    Return a door design row in display mode (for cancel button)
    """
    design = get_object_or_404(Design, id=design_id)
    
    return render(request, 'settings/partials/design_row_display.html', {'design': design})

def update_door_design(request, design_id):
    """
    Process the form submission and update the door design
    """
    design = get_object_or_404(Design, id=design_id)
    
    if request.method == 'POST':
        # Update the design with form data
        design.name = request.POST.get('name')
        design.arch = 'arch' in request.POST
        
        try:
            design.full_clean()  # Validate the model
            design.save()
        except ValidationError as e:
            # Return the edit form with error messages
            context = {
                'design': design,
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/design_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/design_row_display.html', {'design': design})
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

# Edge Profile editing views
def edit_edge_profile(request, profile_id):
    """
    Switch an edge profile row to edit mode
    """
    profile = get_object_or_404(EdgeProfile, id=profile_id)
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'settings/partials/edge_profile_row_edit.html', context)

def get_edge_profile(request, profile_id):
    """
    Return an edge profile row in display mode (for cancel button)
    """
    profile = get_object_or_404(EdgeProfile, id=profile_id)
    
    return render(request, 'settings/partials/edge_profile_row_display.html', {'profile': profile})

def update_edge_profile(request, profile_id):
    """
    Process the form submission and update the edge profile
    """
    profile = get_object_or_404(EdgeProfile, id=profile_id)
    
    if request.method == 'POST':
        # Update the profile with form data
        profile.name = request.POST.get('name')
        
        try:
            profile.full_clean()  # Validate the model
            profile.save()
        except ValidationError as e:
            # Return the edit form with error messages
            context = {
                'profile': profile,
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/edge_profile_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/edge_profile_row_display.html', {'profile': profile})
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

# Panel Rise editing views
def edit_panel_rise(request, rise_id):
    """
    Switch a panel rise row to edit mode
    """
    rise = get_object_or_404(PanelRise, id=rise_id)
    
    context = {
        'rise': rise,
    }
    
    return render(request, 'settings/partials/panel_rise_row_edit.html', context)

def get_panel_rise(request, rise_id):
    """
    Return a panel rise row in display mode (for cancel button)
    """
    rise = get_object_or_404(PanelRise, id=rise_id)
    
    return render(request, 'settings/partials/panel_rise_row_display.html', {'rise': rise})

def update_panel_rise(request, rise_id):
    """
    Process the form submission and update the panel rise
    """
    rise = get_object_or_404(PanelRise, id=rise_id)
    
    if request.method == 'POST':
        # Update the rise with form data
        rise.name = request.POST.get('name')
        
        try:
            rise.full_clean()  # Validate the model
            rise.save()
        except ValidationError as e:
            # Return the edit form with error messages
            context = {
                'rise': rise,
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/panel_rise_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/panel_rise_row_display.html', {'rise': rise})
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

def edit_panel_type(request, type_id):
    """
    Switch a panel type row to edit mode
    """
    type = get_object_or_404(PanelType, id=type_id)
    
    context = {
        'type': type,
    }
    
    return render(request, 'settings/partials/panel_type_row_edit.html', context)

def get_panel_type(request, type_id):
    """
    Return a panel type row in display mode (for cancel button)
    """
    type = get_object_or_404(PanelType, id=type_id)
    
    return render(request, 'settings/partials/panel_type_row_display.html', {'type': type})

def update_panel_type(request, type_id):
    """
    Process the form submission and update the panel type
    """
    panel_type = get_object_or_404(PanelType, id=type_id)
    
    if request.method == 'POST':
        # Update the type with form data
        panel_type.name = request.POST.get('name')
        
        # Handle numeric values with validation
        try:
            panel_type.minimum_sq_ft = Decimal(request.POST.get('minimum_sq_ft', '0'))
            panel_type.surcharge_width = Decimal(request.POST.get('surcharge_width', '0'))
            panel_type.surcharge_height = Decimal(request.POST.get('surcharge_height', '0'))
            panel_type.surcharge_percent = Decimal(request.POST.get('surcharge_percent', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/panel_type_row_edit.html', {
                'type': panel_type,
                'errors': {'surcharge_width': ['Please enter valid numbers for all numeric fields']}
            }, status=422)
        
        panel_type.use_flat_panel_price = 'use_flat_panel_price' in request.POST
        
        try:
            panel_type.full_clean()  # Validate the model
            panel_type.save()
        except ValidationError as e:
            # Return the edit form with error messages
            context = {
                'type': panel_type,
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/panel_type_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/panel_type_row_display.html', {'type': panel_type})
    
    # If not POST request, redirect to door settings
    return redirect('door_settings') 