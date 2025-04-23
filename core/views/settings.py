from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from ..models import Style, PanelType, Design, WoodStock, EdgeProfile, PanelRise, RailDefaults, MiscellaneousDoorSettings
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseBadRequest

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
    misc_settings = MiscellaneousDoorSettings.objects.first()  # Get the first (should be only one) misc settings
    
    context = {
        'styles': styles,
        'wood_stocks': wood_stocks,
        'designs': designs,
        'edge_profiles': edge_profiles,
        'panel_rises': panel_rises,
        'panel_types': panel_types,
        'rail_defaults': rail_defaults,
        'misc_settings': misc_settings,
        'title': 'Door Settings'
    }
    
    return render(request, 'settings/door_settings.html', context)

def drawer_settings(request):
    """
    Render the drawer settings page with all drawer components
    """
    from ..models.drawer import DrawerWoodStock, DrawerEdgeType, DrawerBottomSize, DrawerPricing, DefaultDrawerSettings
    
    wood_stocks = DrawerWoodStock.objects.all()
    edge_types = DrawerEdgeType.objects.all()
    bottom_sizes = DrawerBottomSize.objects.all()
    pricing = DrawerPricing.objects.all()
    drawer_defaults = DefaultDrawerSettings.objects.first()
    
    context = {
        'wood_stocks': wood_stocks,
        'edge_types': edge_types,
        'bottom_sizes': bottom_sizes,
        'pricing': pricing,
        'drawer_defaults': drawer_defaults,
        'title': 'Drawer Settings'
    }
    
    return render(request, 'settings/drawer_settings.html', context)

# Drawer Wood Stock editing views
def edit_drawer_woodstock(request, stock_id):
    """
    Switch a drawer wood stock row to edit mode
    """
    from ..models.drawer import DrawerWoodStock
    wood = get_object_or_404(DrawerWoodStock, id=stock_id)
    
    context = {
        'wood': wood,
    }
    
    return render(request, 'settings/partials/drawer_woodstock_row_edit.html', context)

def get_drawer_woodstock(request, stock_id):
    """
    Return a drawer wood stock row in display mode (for cancel button)
    """
    from ..models.drawer import DrawerWoodStock
    wood = get_object_or_404(DrawerWoodStock, id=stock_id)
    
    return render(request, 'settings/partials/drawer_woodstock_row_display.html', {'wood': wood})

def update_drawer_woodstock(request, stock_id):
    """
    Process the form submission and update the drawer wood stock
    """
    from ..models.drawer import DrawerWoodStock
    from django.core.exceptions import ValidationError
    from decimal import Decimal
    
    wood = get_object_or_404(DrawerWoodStock, id=stock_id)
    
    if request.method == 'POST':
        # Update the wood stock with form data
        wood.name = request.POST.get('name')
        
        # Handle numeric value with validation
        try:
            wood.price = Decimal(request.POST.get('price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_woodstock_row_edit.html', {
                'wood': wood,
                'errors': {'price': ['Please enter a valid number for price']}
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
            return render(request, 'settings/partials/drawer_woodstock_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/drawer_woodstock_row_display.html', {'wood': wood})
    
    # If not POST request, redirect to drawer settings
    return redirect('drawer_settings')

# Drawer Wood Stock add functions
def show_drawer_woodstock_add(request):
    """
    Show the form for adding a new drawer wood stock
    """
    return render(request, 'settings/partials/drawer_woodstock_row_add.html')

def cancel_drawer_woodstock_add(request):
    """
    Cancel adding a new drawer wood stock and return to the button view
    """
    return render(request, 'settings/partials/drawer_woodstock_add_button.html')

def add_drawer_woodstock(request):
    """
    Process the form submission and add a new drawer wood stock
    """
    from ..models.drawer import DrawerWoodStock
    from django.core.exceptions import ValidationError
    from decimal import Decimal
    
    if request.method == 'POST':
        # Create a new wood stock object
        wood = DrawerWoodStock()
        wood.name = request.POST.get('name')
        
        # Handle numeric value with validation
        try:
            wood.price = Decimal(request.POST.get('price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_woodstock_row_add.html', {
                'errors': {'price': ['Please enter a valid number for price']}
            }, status=422)
        
        try:
            wood.full_clean()  # Validate the model
            wood.save()
        except ValidationError as e:
            # Return the add form with error messages
            context = {
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/drawer_woodstock_row_add.html', context, status=422)
        
        # Get all wood stocks to refresh the list
        from ..models.drawer import DrawerWoodStock
        wood_stocks = DrawerWoodStock.objects.all()
        
        # Render all rows including add button
        html = ""
        for wood_item in wood_stocks:
            html += render_to_string('settings/partials/drawer_woodstock_row_display.html', {'wood': wood_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/drawer_woodstock_add_button.html', {}, request)
        
        return HttpResponse(html)
    
    # If not POST request, redirect to drawer settings
    return redirect('drawer_settings')

# Drawer Edge Type editing views
def edit_drawer_edgetype(request, edge_id):
    """
    Switch a drawer edge type row to edit mode
    """
    from ..models.drawer import DrawerEdgeType
    edge = get_object_or_404(DrawerEdgeType, id=edge_id)
    
    context = {
        'edge': edge,
    }
    
    return render(request, 'settings/partials/drawer_edgetype_row_edit.html', context)

def get_drawer_edgetype(request, edge_id):
    """
    Return a drawer edge type row in display mode (for cancel button)
    """
    from ..models.drawer import DrawerEdgeType
    edge = get_object_or_404(DrawerEdgeType, id=edge_id)
    
    return render(request, 'settings/partials/drawer_edgetype_row_display.html', {'edge': edge})

def update_drawer_edgetype(request, edge_id):
    """
    Process the form submission and update the drawer edge type
    """
    from ..models.drawer import DrawerEdgeType
    from django.core.exceptions import ValidationError
    
    edge = get_object_or_404(DrawerEdgeType, id=edge_id)
    
    if request.method == 'POST':
        # Update the edge type with form data
        edge.name = request.POST.get('name')
        
        try:
            edge.full_clean()  # Validate the model
            edge.save()
        except ValidationError as e:
            # Return the edit form with error messages
            context = {
                'edge': edge,
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/drawer_edgetype_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/drawer_edgetype_row_display.html', {'edge': edge})
    
    # If not POST request, redirect to drawer settings
    return redirect('drawer_settings')

# Drawer Edge Type add functions
def show_drawer_edgetype_add(request):
    """
    Show the form for adding a new drawer edge type
    """
    return render(request, 'settings/partials/drawer_edgetype_row_add.html')

def cancel_drawer_edgetype_add(request):
    """
    Cancel adding a new drawer edge type and return to the button view
    """
    return render(request, 'settings/partials/drawer_edgetype_add_button.html')

def add_drawer_edgetype(request):
    """
    Process the form submission and add a new drawer edge type
    """
    from ..models.drawer import DrawerEdgeType
    from django.core.exceptions import ValidationError
    
    if request.method == 'POST':
        # Create a new edge type object
        edge = DrawerEdgeType()
        edge.name = request.POST.get('name')
        
        try:
            edge.full_clean()  # Validate the model
            edge.save()
        except ValidationError as e:
            # Return the add form with error messages
            context = {
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/drawer_edgetype_row_add.html', context, status=422)
        
        # Get all edge types to refresh the list
        from ..models.drawer import DrawerEdgeType
        edge_types = DrawerEdgeType.objects.all()
        
        # Render all rows including add button
        html = ""
        for edge_item in edge_types:
            html += render_to_string('settings/partials/drawer_edgetype_row_display.html', {'edge': edge_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/drawer_edgetype_add_button.html', {}, request)
        
        return HttpResponse(html)
    
    # If not POST request, redirect to drawer settings
    return redirect('drawer_settings')

# Drawer Pricing editing views
def edit_drawer_pricing(request, pricing_id):
    """
    Switch a drawer pricing row to edit mode
    """
    from ..models.drawer import DrawerPricing
    pricing = get_object_or_404(DrawerPricing, id=pricing_id)
    
    context = {
        'pricing': pricing,
    }
    
    return render(request, 'settings/partials/drawer_pricing_row_edit.html', context)

def get_drawer_pricing(request, pricing_id):
    """
    Return a drawer pricing row in display mode (for cancel button)
    """
    from ..models.drawer import DrawerPricing
    pricing = get_object_or_404(DrawerPricing, id=pricing_id)
    
    return render(request, 'settings/partials/drawer_pricing_row_display.html', {'pricing': pricing})

def update_drawer_pricing(request, pricing_id):
    """
    Process the form submission and update the drawer pricing
    """
    from ..models.drawer import DrawerPricing
    from django.core.exceptions import ValidationError
    from decimal import Decimal
    
    pricing = get_object_or_404(DrawerPricing, id=pricing_id)
    
    if request.method == 'POST':
        # Handle numeric values with validation
        try:
            pricing.price = Decimal(request.POST.get('price', '0.01'))
            pricing.height = Decimal(request.POST.get('height', '0.01'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_pricing_row_edit.html', {
                'pricing': pricing,
                'errors': {'price': ['Please enter valid numbers for price and height']}
            }, status=422)
        
        try:
            pricing.full_clean()  # Validate the model
            pricing.save()
        except ValidationError as e:
            # Return the edit form with error messages
            context = {
                'pricing': pricing,
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/drawer_pricing_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/drawer_pricing_row_display.html', {'pricing': pricing})
    
    # If not POST request, redirect to drawer settings
    return redirect('drawer_settings')

# Drawer Pricing add functions
def show_drawer_pricing_add(request):
    """
    Show the form for adding a new drawer pricing configuration
    """
    return render(request, 'settings/partials/drawer_pricing_row_add.html')

def cancel_drawer_pricing_add(request):
    """
    Cancel adding a new drawer pricing configuration and return to the button view
    """
    return render(request, 'settings/partials/drawer_pricing_add_button.html')

def add_drawer_pricing(request):
    """
    Process the form submission and add a new drawer pricing configuration
    """
    from ..models.drawer import DrawerPricing
    from django.core.exceptions import ValidationError
    from decimal import Decimal
    
    if request.method == 'POST':
        # Create a new pricing object
        pricing = DrawerPricing()
        
        # Handle numeric values with validation
        try:
            pricing.price = Decimal(request.POST.get('price', '0.01'))
            pricing.height = Decimal(request.POST.get('height', '0.01'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_pricing_row_add.html', {
                'errors': {'price': ['Please enter valid numbers for price and height']}
            }, status=422)
        
        try:
            pricing.full_clean()  # Validate the model
            pricing.save()
        except ValidationError as e:
            # Return the add form with error messages
            context = {
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/drawer_pricing_row_add.html', context, status=422)
        
        # Get all pricing configs to refresh the list
        from ..models.drawer import DrawerPricing
        pricing_configs = DrawerPricing.objects.all()
        
        # Render all rows including add button
        html = ""
        for pricing_item in pricing_configs:
            html += render_to_string('settings/partials/drawer_pricing_row_display.html', {'pricing': pricing_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/drawer_pricing_add_button.html', {}, request)
        
        return HttpResponse(html)
    
    # If not POST request, redirect to drawer settings
    return redirect('drawer_settings')

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

# Door Style Add Views
def show_door_style_add(request):
    """
    Show the form to add a new door style
    """
    # Get all panel types and designs for the dropdowns
    panel_types = PanelType.objects.all()
    designs = Design.objects.all()
    
    context = {
        'panel_types': panel_types,
        'designs': designs,
    }
    
    return render(request, 'settings/partials/style_row_add.html', context)

def cancel_door_style_add(request):
    """
    Cancel adding a door style and return to the add button
    """
    return render(request, 'settings/partials/style_add_button.html')

def add_door_style(request):
    """
    Process the form submission and create a new door style
    """
    if request.method == 'POST':
        # Create a new style object
        style = Style()
        style.name = request.POST.get('name')
        
        # Set foreign keys
        try:
            style.panel_type_id = int(request.POST.get('panel_type'))
            style.design_id = int(request.POST.get('design'))
        except (ValueError, TypeError):
            # Get all panel types and designs for the dropdowns in case of error
            panel_types = PanelType.objects.all()
            designs = Design.objects.all()
            
            return render(request, 'settings/partials/style_row_add.html', {
                'panel_types': panel_types,
                'designs': designs,
                'errors': {'panel_type': ['Please select valid panel type and design']}
            }, status=422)
        
        # Handle numeric values with validation
        try:
            style.price = Decimal(request.POST.get('price', '0'))
            style.panels_across = int(request.POST.get('panels_across', '1'))
            style.panels_down = int(request.POST.get('panels_down', '1'))
            style.panel_overlap = Decimal(request.POST.get('panel_overlap', '0'))
        except (ValueError, TypeError):
            # Get all panel types and designs for the dropdowns in case of error
            panel_types = PanelType.objects.all()
            designs = Design.objects.all()
            
            return render(request, 'settings/partials/style_row_add.html', {
                'panel_types': panel_types,
                'designs': designs,
                'errors': {'price': ['Please enter valid numbers for all numeric fields']}
            }, status=422)
        
        # Set boolean fields
        style.designs_on_top = 'designs_on_top' in request.POST
        style.designs_on_bottom = 'designs_on_bottom' in request.POST
        
        try:
            style.full_clean()  # Validate the model
            style.save()
        except ValidationError as e:
            # Return the add form with error messages
            # Get all panel types and designs for the dropdowns in case of error
            panel_types = PanelType.objects.all()
            designs = Design.objects.all()
            
            context = {
                'panel_types': panel_types,
                'designs': designs,
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/style_row_add.html', context, status=422)
        
        # Get all styles to refresh the list
        styles = Style.objects.all().select_related('panel_type', 'design')
        
        # Render all rows including add button
        html = ""
        for style_item in styles:
            html += render_to_string('settings/partials/style_row_display.html', {'style': style_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/style_add_button.html', {}, request)
        
        return HttpResponse(html)
    
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

# Wood Stock add functions
def show_wood_stock_add(request):
    """
    Show the form for adding a new wood stock
    """
    return render(request, 'settings/partials/wood_stock_row_add.html')

def cancel_wood_stock_add(request):
    """
    Cancel adding a new wood stock and return to the button view
    """
    return render(request, 'settings/partials/wood_stock_add_button.html')

def add_wood_stock(request):
    """
    Process the form submission and add a new wood stock
    """
    from django.core.exceptions import ValidationError
    from decimal import Decimal
    
    if request.method == 'POST':
        # Create a new wood stock object
        wood = WoodStock()
        wood.name = request.POST.get('name')
        
        # Handle numeric values with validation
        try:
            wood.raised_panel_price = Decimal(request.POST.get('raised_panel_price', '0'))
            wood.flat_panel_price = Decimal(request.POST.get('flat_panel_price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/wood_stock_row_add.html', {
                'errors': {'raised_panel_price': ['Please enter valid numbers for price fields']}
            }, status=422)
        
        try:
            wood.full_clean()  # Validate the model
            wood.save()
        except ValidationError as e:
            # Return the add form with error messages
            context = {
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/wood_stock_row_add.html', context, status=422)
        
        # Get all wood stocks to refresh the list
        wood_stocks = WoodStock.objects.all()
        
        # Render all rows including add button
        html = ""
        for wood_item in wood_stocks:
            html += render_to_string('settings/partials/wood_stock_row_display.html', {'wood': wood_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/wood_stock_add_button.html', {}, request)
        
        return HttpResponse(html)
    
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
    panel_type = get_object_or_404(PanelType, id=type_id)
    
    context = {
        'type': panel_type,
    }
    
    return render(request, 'settings/partials/panel_type_row_edit.html', context)

def get_panel_type(request, type_id):
    """
    Return a panel type row in display mode (for cancel button)
    """
    panel_type = get_object_or_404(PanelType, id=type_id)
    
    return render(request, 'settings/partials/panel_type_row_display.html', {'type': panel_type})

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

# Drawer Bottom Size editing views
def edit_drawer_bottom(request, bottom_id):
    """
    Switch a drawer bottom size row to edit mode
    """
    from ..models.drawer import DrawerBottomSize
    bottom = get_object_or_404(DrawerBottomSize, id=bottom_id)
    
    context = {
        'bottom': bottom,
    }
    
    return render(request, 'settings/partials/drawer_bottom_row_edit.html', context)

def get_drawer_bottom(request, bottom_id):
    """
    Return a drawer bottom size row in display mode (for cancel button)
    """
    from ..models.drawer import DrawerBottomSize
    bottom = get_object_or_404(DrawerBottomSize, id=bottom_id)
    
    return render(request, 'settings/partials/drawer_bottom_row_display.html', {'bottom': bottom})

def update_drawer_bottom(request, bottom_id):
    """
    Process the form submission and update the drawer bottom size
    """
    from ..models.drawer import DrawerBottomSize
    from django.core.exceptions import ValidationError
    from decimal import Decimal
    
    bottom = get_object_or_404(DrawerBottomSize, id=bottom_id)
    
    if request.method == 'POST':
        # Update the bottom size with form data
        bottom.name = request.POST.get('name')
        
        # Handle numeric values with validation
        try:
            bottom.thickness = Decimal(request.POST.get('thickness', '0.001'))
            bottom.price = Decimal(request.POST.get('price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_bottom_row_edit.html', {
                'bottom': bottom,
                'errors': {'thickness': ['Please enter valid numbers for thickness and price']}
            }, status=422)
        
        try:
            bottom.full_clean()  # Validate the model
            bottom.save()
        except ValidationError as e:
            # Return the edit form with error messages
            context = {
                'bottom': bottom,
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/drawer_bottom_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/drawer_bottom_row_display.html', {'bottom': bottom})
    
    # If not POST request, redirect to drawer settings
    return redirect('drawer_settings')

# Drawer Bottom Size add functions
def show_drawer_bottom_add(request):
    """
    Show the form for adding a new drawer bottom size
    """
    return render(request, 'settings/partials/drawer_bottom_row_add.html')

def cancel_drawer_bottom_add(request):
    """
    Cancel adding a new drawer bottom size and return to the button view
    """
    return render(request, 'settings/partials/drawer_bottom_add_button.html')

def add_drawer_bottom(request):
    """
    Process the form submission and add a new drawer bottom size
    """
    from ..models.drawer import DrawerBottomSize
    from django.core.exceptions import ValidationError
    from decimal import Decimal
    
    if request.method == 'POST':
        # Create a new bottom size object
        bottom = DrawerBottomSize()
        bottom.name = request.POST.get('name')
        
        # Handle numeric values with validation
        try:
            bottom.thickness = Decimal(request.POST.get('thickness', '0.001'))
            bottom.price = Decimal(request.POST.get('price', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/drawer_bottom_row_add.html', {
                'errors': {'thickness': ['Please enter valid numbers for thickness and price']}
            }, status=422)
        
        try:
            bottom.full_clean()  # Validate the model
            bottom.save()
        except ValidationError as e:
            # Return the add form with error messages
            context = {
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/drawer_bottom_row_add.html', context, status=422)
        
        # Get all bottom sizes to refresh the list
        from ..models.drawer import DrawerBottomSize
        bottom_sizes = DrawerBottomSize.objects.all()
        
        # Render all rows including add button
        html = ""
        for bottom_item in bottom_sizes:
            html += render_to_string('settings/partials/drawer_bottom_row_display.html', {'bottom': bottom_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/drawer_bottom_add_button.html', {}, request)
        
        return HttpResponse(html)
    
    # If not POST request, redirect to drawer settings
    return redirect('drawer_settings')

# Rail Defaults editing views
def edit_rail_defaults(request):
    """
    Switch rail defaults row to edit mode
    """
    defaults = RailDefaults.objects.first()
    
    if not defaults:
        # Create default values if they don't exist
        defaults = RailDefaults.objects.create(
            top=Decimal('2.50'),
            bottom=Decimal('2.50'),
            left=Decimal('2.50'),
            right=Decimal('2.50')
        )
    
    context = {
        'defaults': defaults,
    }
    
    return render(request, 'settings/partials/rail_defaults_row_edit.html', context)

def get_rail_defaults(request):
    """
    Return rail defaults row in display mode (for cancel button)
    """
    defaults = RailDefaults.objects.first()
    
    if not defaults:
        # Create default values if they don't exist
        defaults = RailDefaults.objects.create(
            top=Decimal('2.50'),
            bottom=Decimal('2.50'),
            left=Decimal('2.50'),
            right=Decimal('2.50')
        )
    
    return render(request, 'settings/partials/rail_defaults_row_display.html', {'defaults': defaults})

def update_rail_defaults(request):
    """
    Process the form submission and update the rail defaults
    """
    defaults = RailDefaults.objects.first()
    
    if not defaults:
        # Create default values if they don't exist
        defaults = RailDefaults.objects.create(
            top=Decimal('2.50'),
            bottom=Decimal('2.50'),
            left=Decimal('2.50'),
            right=Decimal('2.50')
        )
    
    if request.method == 'POST':
        # Update the defaults with form data
        try:
            defaults.top = Decimal(request.POST.get('top', '2.50'))
            defaults.bottom = Decimal(request.POST.get('bottom', '2.50'))
            defaults.left = Decimal(request.POST.get('left', '2.50'))
            defaults.right = Decimal(request.POST.get('right', '2.50'))
            
            defaults.full_clean()  # Validate the model
            defaults.save()
        except (ValidationError, ValueError) as e:
            # Return the edit form with error messages
            if isinstance(e, ValidationError):
                errors = e.message_dict
            else:
                errors = {'top': ['Invalid decimal value']}
                
            context = {
                'defaults': defaults,
                'errors': errors
            }
            return render(request, 'settings/partials/rail_defaults_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/rail_defaults_row_display.html', {'defaults': defaults})
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

# Door Design Add Views
def show_door_design_add(request):
    """
    Show the form to add a new door design
    """
    return render(request, 'settings/partials/door_design_row_add.html')

def cancel_door_design_add(request):
    """
    Cancel adding a door design and return to the add button
    """
    return render(request, 'settings/partials/door_design_add_button.html')

def add_door_design(request):
    """
    Process the form submission and create a new door design
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        arch = 'arch' in request.POST
        
        design = Design(name=name, arch=arch)
        
        try:
            design.full_clean()  # Validate the model
            design.save()
        except ValidationError as e:
            # Return the add form with error messages
            context = {
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/door_design_row_add.html', context, status=422)
        
        # Get all designs to refresh the list
        designs = Design.objects.all().order_by('name')
        
        # Render all rows including add button
        html = ""
        for design_item in designs:
            html += render_to_string('settings/partials/design_row_display.html', {'design': design_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/door_design_add_button.html', {}, request)
        
        return HttpResponse(html)
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

# Edge Profile Add Views
def show_edge_profile_add(request):
    """
    Show the form to add a new edge profile
    """
    return render(request, 'settings/partials/edge_profile_row_add.html')

def cancel_edge_profile_add(request):
    """
    Cancel adding an edge profile and return to the add button
    """
    return render(request, 'settings/partials/edge_profile_add_button.html')

def add_edge_profile(request):
    """
    Process the form submission and create a new edge profile
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        
        profile = EdgeProfile(name=name)
        
        try:
            profile.full_clean()  # Validate the model
            profile.save()
        except ValidationError as e:
            # Return the add form with error messages
            context = {
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/edge_profile_row_add.html', context, status=422)
        
        # Get all edge profiles to refresh the list
        profiles = EdgeProfile.objects.all().order_by('name')
        
        # Render all rows including add button
        html = ""
        for profile_item in profiles:
            html += render_to_string('settings/partials/edge_profile_row_display.html', {'profile': profile_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/edge_profile_add_button.html', {}, request)
        
        return HttpResponse(html)
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

# Panel Type Add Views
def show_panel_type_add(request):
    """
    Show the form to add a new panel type
    """
    return render(request, 'settings/partials/panel_type_row_add.html')

def cancel_panel_type_add(request):
    """
    Cancel adding a panel type and return to the add button
    """
    return render(request, 'settings/partials/panel_type_add_button.html')

def add_panel_type(request):
    """
    Process the form submission and create a new panel type
    """
    if request.method == 'POST':
        # Create a new panel type object
        panel_type = PanelType()
        panel_type.name = request.POST.get('name')
        
        # Handle numeric values with validation
        try:
            panel_type.minimum_sq_ft = Decimal(request.POST.get('minimum_sq_ft', '0'))
            panel_type.surcharge_width = Decimal(request.POST.get('surcharge_width', '0'))
            panel_type.surcharge_height = Decimal(request.POST.get('surcharge_height', '0'))
            panel_type.surcharge_percent = Decimal(request.POST.get('surcharge_percent', '0'))
        except (ValueError, TypeError):
            return render(request, 'settings/partials/panel_type_row_add.html', {
                'errors': {'surcharge_width': ['Please enter valid numbers for all numeric fields']}
            }, status=422)
        
        panel_type.use_flat_panel_price = 'use_flat_panel_price' in request.POST
        
        try:
            panel_type.full_clean()  # Validate the model
            panel_type.save()
        except ValidationError as e:
            # Return the add form with error messages
            context = {
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/panel_type_row_add.html', context, status=422)
        
        # Get all panel types to refresh the list
        panel_types = PanelType.objects.all().order_by('name')
        
        # Render all rows including add button
        html = ""
        for panel_type_item in panel_types:
            html += render_to_string('settings/partials/panel_type_row_display.html', {'type': panel_type_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/panel_type_add_button.html', {}, request)
        
        return HttpResponse(html)
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

# Panel Rise Add Views
def show_panel_rise_add(request):
    """
    Show the form to add a new panel rise
    """
    return render(request, 'settings/partials/panel_rise_row_add.html')

def cancel_panel_rise_add(request):
    """
    Cancel adding a panel rise and return to the add button
    """
    return render(request, 'settings/partials/panel_rise_add_button.html')

def add_panel_rise(request):
    """
    Process the form submission and create a new panel rise
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        
        rise = PanelRise(name=name)
        
        try:
            rise.full_clean()  # Validate the model
            rise.save()
        except ValidationError as e:
            # Return the add form with error messages
            context = {
                'errors': e.message_dict
            }
            return render(request, 'settings/partials/panel_rise_row_add.html', context, status=422)
        
        # Get all panel rises to refresh the list
        rises = PanelRise.objects.all().order_by('name')
        
        # Render all rows including add button
        html = ""
        for rise_item in rises:
            html += render_to_string('settings/partials/panel_rise_row_display.html', {'rise': rise_item}, request)
        
        # Add the "add button" row at the end
        html += render_to_string('settings/partials/panel_rise_add_button.html', {}, request)
        
        return HttpResponse(html)
    
    # If not POST request, redirect to door settings
    return redirect('door_settings')

# Drawer Default Settings editing views
def edit_drawer_defaults(request):
    """
    Switch the drawer default settings row to edit mode
    """
    from ..models.drawer import DefaultDrawerSettings
    defaults = DefaultDrawerSettings.objects.first()
    
    if not defaults:
        defaults = DefaultDrawerSettings.objects.create()
    
    context = {
        'defaults': defaults,
    }
    
    return render(request, 'settings/partials/drawer_defaults_row_edit.html', context)

def get_drawer_defaults(request):
    """
    Return the drawer default settings row in display mode (for cancel button)
    """
    from ..models.drawer import DefaultDrawerSettings
    defaults = DefaultDrawerSettings.objects.first()
    
    if not defaults:
        defaults = DefaultDrawerSettings.objects.create()
    
    return render(request, 'settings/partials/drawer_defaults_row_display.html', {'defaults': defaults})

def update_drawer_defaults(request):
    """
    Update the drawer default settings
    """
    from ..models.drawer import DefaultDrawerSettings
    
    if request.method == 'POST':
        defaults = DefaultDrawerSettings.objects.first()
        
        if not defaults:
            defaults = DefaultDrawerSettings.objects.create()
        
        defaults.surcharge_width = request.POST.get('surcharge_width', 0.00)
        defaults.surcharge_depth = request.POST.get('surcharge_depth', 0.00)
        defaults.surcharge_percent = request.POST.get('surcharge_percent', 0.00)
        defaults.finish_charge = request.POST.get('finish_charge', 0.00)
        defaults.undermount_charge = request.POST.get('undermount_charge', 0.00)
        defaults.ends_cutting_adjustment = request.POST.get('ends_cutting_adjustment', 0.000)
        defaults.sides_cutting_adjustment = request.POST.get('sides_cutting_adjustment', 0.000)
        defaults.plywood_size_adjustment = request.POST.get('plywood_size_adjustment', 0.000)
        defaults.save()
        
        return render(request, 'settings/partials/drawer_defaults_row_display.html', {'defaults': defaults})
    
    return HttpResponseBadRequest("Invalid request method")

def edit_misc_settings(request):
    """
    Switch miscellaneous door settings row to edit mode
    """
    settings = MiscellaneousDoorSettings.objects.first()
    panel_types = PanelType.objects.all()
    
    if not settings:
        # Create default values if they don't exist
        settings = MiscellaneousDoorSettings.objects.create(
            extra_height=Decimal('0.125'),
            extra_width=Decimal('0.125'),
            glue_min_width=Decimal('8.000'),
            rail_extra=Decimal('0.125'),
            drawer_front=PanelType.objects.first(),
            drawer_slab=PanelType.objects.first()
        )
    
    context = {
        'settings': settings,
        'panel_types': panel_types,
    }
    
    return render(request, 'settings/partials/misc_settings_row_edit.html', context)

def get_misc_settings(request):
    """
    Return miscellaneous door settings row in display mode
    """
    settings = MiscellaneousDoorSettings.objects.first()
    
    if not settings:
        # Create default values if they don't exist
        settings = MiscellaneousDoorSettings.objects.create(
            extra_height=Decimal('0.125'),
            extra_width=Decimal('0.125'),
            glue_min_width=Decimal('8.000'),
            rail_extra=Decimal('0.125'),
            drawer_front=PanelType.objects.first(),
            drawer_slab=PanelType.objects.first()
        )
    
    return render(request, 'settings/partials/misc_settings_row_display.html', {'settings': settings})

def update_misc_settings(request):
    """
    Process the form submission and update the miscellaneous door settings
    """
    settings = MiscellaneousDoorSettings.objects.first()
    panel_types = PanelType.objects.all()
    
    if not settings:
        settings = MiscellaneousDoorSettings.objects.create(
            extra_height=Decimal('0.125'),
            extra_width=Decimal('0.125'),
            glue_min_width=Decimal('8.000'),
            rail_extra=Decimal('0.125'),
            drawer_front=PanelType.objects.first(),
            drawer_slab=PanelType.objects.first()
        )
    
    if request.method == 'POST':
        try:
            # Update decimal fields
            settings.extra_height = Decimal(request.POST.get('extra_height', '0.125'))
            settings.extra_width = Decimal(request.POST.get('extra_width', '0.125'))
            settings.glue_min_width = Decimal(request.POST.get('glue_min_width', '8.000'))
            settings.rail_extra = Decimal(request.POST.get('rail_extra', '0.125'))
            
            # Update foreign key fields
            settings.drawer_front_id = request.POST.get('drawer_front')
            settings.drawer_slab_id = request.POST.get('drawer_slab')
            
            settings.full_clean()  # Validate the model
            settings.save()
        except (ValidationError, InvalidOperation) as e:
            # Return the edit form with error messages
            if isinstance(e, ValidationError):
                errors = e.message_dict
            else:
                errors = {'extra_height': ['Invalid decimal value']}
                
            context = {
                'settings': settings,
                'panel_types': panel_types,
                'errors': errors
            }
            return render(request, 'settings/partials/misc_settings_row_edit.html', context, status=422)
        
        # Return the updated row in display mode
        return render(request, 'settings/partials/misc_settings_row_display.html', {'settings': settings})
    
    # If not POST request, redirect to door settings
    return redirect('door_settings') 