#!/usr/bin/env python
"""
Script to create default settings for drawer settings and rail defaults.
This script should be run once during initial setup of the application.
"""
import os
import sys
import django
from decimal import Decimal

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DoorsAndDrawers.settings')
django.setup()

# Import after Django setup
from core.models.drawer import DefaultDrawerSettings
from core.models.door import (
    RailDefaults, MiscellaneousDoorSettings, PanelType,
    WoodStock, Design, EdgeProfile, PanelRise, Style
)


def create_drawer_defaults():
    """Create default settings for drawers if they don't exist."""
    if DefaultDrawerSettings.objects.exists():
        print("Drawer default settings already exist. Skipping creation.")
        return DefaultDrawerSettings.objects.first()

    # Create with sensible default values
    drawer_defaults = DefaultDrawerSettings.objects.create(
        surcharge_width=Decimal('24.00'),
        surcharge_depth=Decimal('24.00'),
        surcharge_percent=Decimal('15.00'),
        finish_charge=Decimal('11.00'),
        undermount_charge=Decimal('2.50'),
        ends_cutting_adjustment=Decimal('0.000'),
        sides_cutting_adjustment=Decimal('0.375'),
        plywood_size_adjustment=Decimal('0.750')
    )

    print(f"Created drawer default settings: {drawer_defaults}")
    return drawer_defaults


def create_rail_defaults():
    """Create default rail settings for doors if they don't exist."""
    if RailDefaults.objects.exists():
        print("Rail defaults already exist. Skipping creation.")
        return RailDefaults.objects.first()

    # Create with standard rail sizes
    rail_defaults = RailDefaults.objects.create(
        top=Decimal('2.250'),     # 2-1/4"
        bottom=Decimal('2.250'),  # 2-1/4"
        left=Decimal('2.250'),    # 2-1/4"
        right=Decimal('2.250'),   # 2-1/4"
        interior_rail_size=Decimal('2.250')  # 2-1/4"
    )

    print(f"Created rail defaults: {rail_defaults}")
    return rail_defaults


def create_door_defaults():
    """Create default miscellaneous door settings if they don't exist."""
    if MiscellaneousDoorSettings.objects.exists():
        print("Door default settings already exist. Skipping creation.")
        return MiscellaneousDoorSettings.objects.first()

    # Ensure we have at least one PanelType for the foreign key references
    if not PanelType.objects.exists():
        print("No PanelType objects found. Creating basic panel types...")
        # Create basic panel types for drawer fronts and slabs
        flat_panel = PanelType.objects.create(
            name="Flat Panel",
            surcharge_width=Decimal('0.00'),
            surcharge_height=Decimal('0.00'),
            surcharge_percent=Decimal('0.00'),
            minimum_sq_ft=Decimal('0.00'),
            use_flat_panel_price=True
        )
        raised_panel = PanelType.objects.create(
            name="Raised Panel",
            surcharge_width=Decimal('0.00'),
            surcharge_height=Decimal('0.00'),
            surcharge_percent=Decimal('0.00'),
            minimum_sq_ft=Decimal('0.00'),
            use_flat_panel_price=False
        )
        print(f"Created basic panel types: {flat_panel.name}, {raised_panel.name}")

    # Get the first available panel type for drawer references
    default_panel_type = PanelType.objects.first()

    # Create with sensible default values
    door_defaults = MiscellaneousDoorSettings.objects.create(
        extra_height=Decimal('0.125'),      # 1/8" extra height
        extra_width=Decimal('0.125'),       # 1/8" extra width
        glue_min_width=Decimal('6.000'),    # 6" minimum width for gluing
        rail_extra=Decimal('0.125'),        # 1/8" rail joint extra
        drawer_front=default_panel_type,
        drawer_slab=default_panel_type
    )

    print(f"Created door default settings: {door_defaults}")
    return door_defaults


def create_design_defaults():
    """Create default door designs if they don't exist."""
    if Design.objects.exists():
        print("Door designs already exist. Skipping creation.")
        return

    # Create common door designs
    designs = [
        {"name": "Square", "arch": False},
        {"name": "Arch", "arch": True},
        {"name": "Cathedral", "arch": True},
        {"name": "Roman", "arch": True},
    ]

    created_designs = []
    for design_data in designs:
        design = Design.objects.create(**design_data)
        created_designs.append(design)
        print(f"Created design: {design.name}")

    return created_designs


def create_edge_profile_defaults():
    """Create default edge profiles if they don't exist."""
    if EdgeProfile.objects.exists():
        print("Edge profiles already exist. Skipping creation.")
        return

    # Create common edge profiles (E1, E2, etc.)
    edge_profiles = ["E1", "E2", "E3", "E4", "E5", "E6"]

    created_profiles = []
    for profile_name in edge_profiles:
        profile = EdgeProfile.objects.create(name=profile_name)
        created_profiles.append(profile)
        print(f"Created edge profile: {profile.name}")

    return created_profiles


def create_panel_rise_defaults():
    """Create default panel rise options if they don't exist."""
    if PanelRise.objects.exists():
        print("Panel rise options already exist. Skipping creation.")
        return

    # Create common panel rise options
    panel_rises = [
        "1/8 inch",
        "1/4 inch", 
        "3/8 inch",
        "1/2 inch",
        "5/8 inch",
        "3/4 inch"
    ]

    created_rises = []
    for rise_name in panel_rises:
        rise = PanelRise.objects.create(name=rise_name)
        created_rises.append(rise)
        print(f"Created panel rise: {rise.name}")

    return created_rises


def create_woodstock_defaults():
    """Create default wood stock options if they don't exist."""
    if WoodStock.objects.exists():
        print("Wood stock options already exist. Skipping creation.")
        return

    # Create common wood stock options with pricing
    woodstocks = [
        {"name": "Oak", "raised_panel_price": Decimal('12.50'), "flat_panel_price": Decimal('10.00')},
        {"name": "Maple", "raised_panel_price": Decimal('14.00'), "flat_panel_price": Decimal('11.50')},
        {"name": "Cherry", "raised_panel_price": Decimal('16.00'), "flat_panel_price": Decimal('13.50')},
        {"name": "Pine", "raised_panel_price": Decimal('8.50'), "flat_panel_price": Decimal('7.00')},
        {"name": "Birch", "raised_panel_price": Decimal('13.00'), "flat_panel_price": Decimal('10.50')},
    ]

    created_stocks = []
    for stock_data in woodstocks:
        stock = WoodStock.objects.create(**stock_data)
        created_stocks.append(stock)
        print(f"Created wood stock: {stock.name} (Raised: ${stock.raised_panel_price}, Flat: ${stock.flat_panel_price})")

    return created_stocks


def create_style_defaults():
    """Create default door styles if they don't exist."""
    if Style.objects.exists():
        print("Door styles already exist. Skipping creation.")
        return

    # Ensure we have required dependencies
    if not PanelType.objects.exists():
        print("No PanelType objects found. Creating them first...")
        create_door_defaults()  # This will create PanelType objects

    if not Design.objects.exists():
        print("No Design objects found. Creating them first...")
        create_design_defaults()

    # Get default panel types and designs
    flat_panel = PanelType.objects.filter(use_flat_panel_price=True).first()
    raised_panel = PanelType.objects.filter(use_flat_panel_price=False).first()
    square_design = Design.objects.filter(arch=False).first()
    arch_design = Design.objects.filter(arch=True).first()

    # Create common door styles
    styles = [
        {
            "name": "ATFP", 
            "panel_type": flat_panel,
            "design": square_design,
            "price": Decimal('25.00'),
            "panels_across": 1,
            "panels_down": 1,
            "panel_overlap": Decimal('0.125'),
            "designs_on_top": False,
            "designs_on_bottom": False
        },
        {
            "name": "ATRP", 
            "panel_type": raised_panel,
            "design": square_design,
            "price": Decimal('35.00'),
            "panels_across": 1,
            "panels_down": 1,
            "panel_overlap": Decimal('0.125'),
            "designs_on_top": False,
            "designs_on_bottom": False
        },
        {
            "name": "CTF", 
            "panel_type": flat_panel,
            "design": arch_design or square_design,
            "price": Decimal('45.00'),
            "panels_across": 1,
            "panels_down": 1,
            "panel_overlap": Decimal('0.125'),
            "designs_on_top": True,
            "designs_on_bottom": False
        },
    ]

    created_styles = []
    for style_data in styles:
        if style_data["panel_type"] and style_data["design"]:  # Only create if dependencies exist
            style = Style.objects.create(**style_data)
            created_styles.append(style)
            print(f"Created style: {style.name} - {style.panel_type.name} - {style.design.name}")

    return created_styles


def main():
    """Main function to create all default settings."""
    print("Creating default settings...")

    # Create basic settings
    drawer_defaults = create_drawer_defaults()
    rail_defaults = create_rail_defaults()
    door_defaults = create_door_defaults()

    # Create door-related default data
    print("\nCreating door-related default data...")
    designs = create_design_defaults()
    edge_profiles = create_edge_profile_defaults()
    panel_rises = create_panel_rise_defaults()
    woodstocks = create_woodstock_defaults()
    styles = create_style_defaults()

    print("\nSummary:")
    print(f"Drawer Default Settings: ID={drawer_defaults.id}")
    print(f"Rail Defaults: ID={rail_defaults.id}")
    print(f"Door Default Settings: ID={door_defaults.id}")

    # Count created items
    design_count = Design.objects.count()
    edge_profile_count = EdgeProfile.objects.count()
    panel_rise_count = PanelRise.objects.count()
    woodstock_count = WoodStock.objects.count()
    style_count = Style.objects.count()

    print(f"Door Designs: {design_count} total")
    print(f"Edge Profiles: {edge_profile_count} total")
    print(f"Panel Rise Options: {panel_rise_count} total")
    print(f"Wood Stock Options: {woodstock_count} total")
    print(f"Door Styles: {style_count} total")
    print("\nDefault settings creation completed successfully.")


if __name__ == "__main__":
    main() 
