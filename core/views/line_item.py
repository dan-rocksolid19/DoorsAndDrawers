from django.shortcuts import render
from ..models.door import WoodStock, Design, PanelType, EdgeProfile, PanelRise, Style

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
