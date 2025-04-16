from django.urls import path
from ..views.settings import (
    door_settings, drawer_settings,
    edit_door_style, get_door_style, update_door_style,
    show_door_style_add, cancel_door_style_add, add_door_style,
    edit_wood_stock, get_wood_stock, update_wood_stock,
    show_wood_stock_add, cancel_wood_stock_add, add_wood_stock,
    edit_door_design, get_door_design, update_door_design,
    show_door_design_add, cancel_door_design_add, add_door_design,
    edit_edge_profile, get_edge_profile, update_edge_profile,
    show_edge_profile_add, cancel_edge_profile_add, add_edge_profile,
    edit_panel_rise, get_panel_rise, update_panel_rise,
    show_panel_rise_add, cancel_panel_rise_add, add_panel_rise,
    edit_panel_type, get_panel_type, update_panel_type,
    show_panel_type_add, cancel_panel_type_add, add_panel_type,
    edit_rail_defaults, get_rail_defaults, update_rail_defaults,
    edit_drawer_woodstock, get_drawer_woodstock, update_drawer_woodstock,
    edit_drawer_edgetype, get_drawer_edgetype, update_drawer_edgetype,
    edit_drawer_bottom, get_drawer_bottom, update_drawer_bottom,
    edit_drawer_pricing, get_drawer_pricing, update_drawer_pricing,
    show_drawer_woodstock_add, cancel_drawer_woodstock_add, add_drawer_woodstock,
    show_drawer_edgetype_add, cancel_drawer_edgetype_add, add_drawer_edgetype,
    show_drawer_bottom_add, cancel_drawer_bottom_add, add_drawer_bottom,
    show_drawer_pricing_add, cancel_drawer_pricing_add, add_drawer_pricing,
    edit_drawer_defaults, get_drawer_defaults, update_drawer_defaults
)

urlpatterns = [
    path('doors/', door_settings, name='door_settings'),
    path('drawers/', drawer_settings, name='drawer_settings'),
    
    # Door Style URLs
    path('doors/styles/<int:style_id>/edit/', edit_door_style, name='edit_door_style'),
    path('doors/styles/<int:style_id>/', get_door_style, name='get_door_style'),
    path('doors/styles/<int:style_id>/update/', update_door_style, name='update_door_style'),
    path('doors/styles/add/show/', show_door_style_add, name='show_door_style_add'),
    path('doors/styles/add/cancel/', cancel_door_style_add, name='cancel_door_style_add'),
    path('doors/styles/add/', add_door_style, name='add_door_style'),
    
    # Wood Stock URLs
    path('doors/wood-stock/<int:stock_id>/edit/', edit_wood_stock, name='edit_wood_stock'),
    path('doors/wood-stock/<int:stock_id>/', get_wood_stock, name='get_wood_stock'),
    path('doors/wood-stock/<int:stock_id>/update/', update_wood_stock, name='update_wood_stock'),
    path('doors/wood-stock/add/show/', show_wood_stock_add, name='show_wood_stock_add'),
    path('doors/wood-stock/add/cancel/', cancel_wood_stock_add, name='cancel_wood_stock_add'),
    path('doors/wood-stock/add/', add_wood_stock, name='add_wood_stock'),
    
    # Drawer Wood Stock URLs
    path('drawers/wood-stock/<int:stock_id>/edit/', edit_drawer_woodstock, name='edit_drawer_woodstock'),
    path('drawers/wood-stock/<int:stock_id>/', get_drawer_woodstock, name='get_drawer_woodstock'),
    path('drawers/wood-stock/<int:stock_id>/update/', update_drawer_woodstock, name='update_drawer_woodstock'),
    path('drawers/wood-stock/add/show/', show_drawer_woodstock_add, name='show_drawer_woodstock_add'),
    path('drawers/wood-stock/add/cancel/', cancel_drawer_woodstock_add, name='cancel_drawer_woodstock_add'),
    path('drawers/wood-stock/add/', add_drawer_woodstock, name='add_drawer_woodstock'),
    
    # Drawer Edge Type URLs
    path('drawers/edge-types/<int:edge_id>/edit/', edit_drawer_edgetype, name='edit_drawer_edgetype'),
    path('drawers/edge-types/<int:edge_id>/', get_drawer_edgetype, name='get_drawer_edgetype'),
    path('drawers/edge-types/<int:edge_id>/update/', update_drawer_edgetype, name='update_drawer_edgetype'),
    path('drawers/edge-types/add/show/', show_drawer_edgetype_add, name='show_drawer_edgetype_add'),
    path('drawers/edge-types/add/cancel/', cancel_drawer_edgetype_add, name='cancel_drawer_edgetype_add'),
    path('drawers/edge-types/add/', add_drawer_edgetype, name='add_drawer_edgetype'),
    
    # Drawer Bottom Size URLs
    path('drawers/bottom-sizes/<int:bottom_id>/edit/', edit_drawer_bottom, name='edit_drawer_bottom'),
    path('drawers/bottom-sizes/<int:bottom_id>/', get_drawer_bottom, name='get_drawer_bottom'),
    path('drawers/bottom-sizes/<int:bottom_id>/update/', update_drawer_bottom, name='update_drawer_bottom'),
    path('drawers/bottom-sizes/add/show/', show_drawer_bottom_add, name='show_drawer_bottom_add'),
    path('drawers/bottom-sizes/add/cancel/', cancel_drawer_bottom_add, name='cancel_drawer_bottom_add'),
    path('drawers/bottom-sizes/add/', add_drawer_bottom, name='add_drawer_bottom'),
    
    # Drawer Pricing URLs
    path('drawers/pricing/<int:pricing_id>/edit/', edit_drawer_pricing, name='edit_drawer_pricing'),
    path('drawers/pricing/<int:pricing_id>/', get_drawer_pricing, name='get_drawer_pricing'),
    path('drawers/pricing/<int:pricing_id>/update/', update_drawer_pricing, name='update_drawer_pricing'),
    path('drawers/pricing/add/show/', show_drawer_pricing_add, name='show_drawer_pricing_add'),
    path('drawers/pricing/add/cancel/', cancel_drawer_pricing_add, name='cancel_drawer_pricing_add'),
    path('drawers/pricing/add/', add_drawer_pricing, name='add_drawer_pricing'),
    
    # Door Design URLs
    path('doors/designs/<int:design_id>/edit/', edit_door_design, name='edit_door_design'),
    path('doors/designs/<int:design_id>/', get_door_design, name='get_door_design'),
    path('doors/designs/<int:design_id>/update/', update_door_design, name='update_door_design'),
    path('doors/designs/add/show/', show_door_design_add, name='show_door_design_add'),
    path('doors/designs/add/cancel/', cancel_door_design_add, name='cancel_door_design_add'),
    path('doors/designs/add/', add_door_design, name='add_door_design'),
    
    # Edge Profile URLs
    path('doors/edge-profiles/<int:profile_id>/edit/', edit_edge_profile, name='edit_edge_profile'),
    path('doors/edge-profiles/<int:profile_id>/', get_edge_profile, name='get_edge_profile'),
    path('doors/edge-profiles/<int:profile_id>/update/', update_edge_profile, name='update_edge_profile'),
    path('doors/edge-profiles/add/show/', show_edge_profile_add, name='show_edge_profile_add'),
    path('doors/edge-profiles/add/cancel/', cancel_edge_profile_add, name='cancel_edge_profile_add'),
    path('doors/edge-profiles/add/', add_edge_profile, name='add_edge_profile'),
    
    # Panel Rise URLs
    path('doors/panel-rises/<int:rise_id>/edit/', edit_panel_rise, name='edit_panel_rise'),
    path('doors/panel-rises/<int:rise_id>/', get_panel_rise, name='get_panel_rise'),
    path('doors/panel-rises/<int:rise_id>/update/', update_panel_rise, name='update_panel_rise'),
    path('doors/panel-rises/add/show/', show_panel_rise_add, name='show_panel_rise_add'),
    path('doors/panel-rises/add/cancel/', cancel_panel_rise_add, name='cancel_panel_rise_add'),
    path('doors/panel-rises/add/', add_panel_rise, name='add_panel_rise'),
    
    # Panel Type URLs
    path('doors/panel-types/<int:type_id>/edit/', edit_panel_type, name='edit_panel_type'),
    path('doors/panel-types/<int:type_id>/', get_panel_type, name='get_panel_type'),
    path('doors/panel-types/<int:type_id>/update/', update_panel_type, name='update_panel_type'),
    path('doors/panel-types/add/show/', show_panel_type_add, name='show_panel_type_add'),
    path('doors/panel-types/add/cancel/', cancel_panel_type_add, name='cancel_panel_type_add'),
    path('doors/panel-types/add/', add_panel_type, name='add_panel_type'),
    
    # Rail Defaults URLs
    path('doors/rail-defaults/edit/', edit_rail_defaults, name='edit_rail_defaults'),
    path('doors/rail-defaults/', get_rail_defaults, name='get_rail_defaults'),
    path('doors/rail-defaults/update/', update_rail_defaults, name='update_rail_defaults'),
    
    # Drawer Default Settings URLs
    path('drawers/defaults/edit/', edit_drawer_defaults, name='edit_drawer_defaults'),
    path('drawers/defaults/', get_drawer_defaults, name='get_drawer_defaults'),
    path('drawers/defaults/update/', update_drawer_defaults, name='update_drawer_defaults'),
] 