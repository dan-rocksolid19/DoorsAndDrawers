from django.urls import path
from ..views.settings import (
    door_settings, 
    edit_door_style, get_door_style, update_door_style,
    edit_wood_stock, get_wood_stock, update_wood_stock,
    edit_door_design, get_door_design, update_door_design,
    edit_edge_profile, get_edge_profile, update_edge_profile,
    edit_panel_rise, get_panel_rise, update_panel_rise,
    edit_panel_type, get_panel_type, update_panel_type
)

urlpatterns = [
    path('doors/', door_settings, name='door_settings'),
    
    # Door Style URLs
    path('doors/styles/<int:style_id>/edit/', edit_door_style, name='edit_door_style'),
    path('doors/styles/<int:style_id>/', get_door_style, name='get_door_style'),
    path('doors/styles/<int:style_id>/update/', update_door_style, name='update_door_style'),
    
    # Wood Stock URLs
    path('doors/wood-stock/<int:stock_id>/edit/', edit_wood_stock, name='edit_wood_stock'),
    path('doors/wood-stock/<int:stock_id>/', get_wood_stock, name='get_wood_stock'),
    path('doors/wood-stock/<int:stock_id>/update/', update_wood_stock, name='update_wood_stock'),
    
    # Door Design URLs
    path('doors/designs/<int:design_id>/edit/', edit_door_design, name='edit_door_design'),
    path('doors/designs/<int:design_id>/', get_door_design, name='get_door_design'),
    path('doors/designs/<int:design_id>/update/', update_door_design, name='update_door_design'),
    
    # Edge Profile URLs
    path('doors/edge-profiles/<int:profile_id>/edit/', edit_edge_profile, name='edit_edge_profile'),
    path('doors/edge-profiles/<int:profile_id>/', get_edge_profile, name='get_edge_profile'),
    path('doors/edge-profiles/<int:profile_id>/update/', update_edge_profile, name='update_edge_profile'),
    
    # Panel Rise URLs
    path('doors/panel-rises/<int:rise_id>/edit/', edit_panel_rise, name='edit_panel_rise'),
    path('doors/panel-rises/<int:rise_id>/', get_panel_rise, name='get_panel_rise'),
    path('doors/panel-rises/<int:rise_id>/update/', update_panel_rise, name='update_panel_rise'),
    
    # Panel Type URLs
    path('doors/panel-types/<int:type_id>/edit/', edit_panel_type, name='edit_panel_type'),
    path('doors/panel-types/<int:type_id>/', get_panel_type, name='get_panel_type'),
    path('doors/panel-types/<int:type_id>/update/', update_panel_type, name='update_panel_type'),
] 