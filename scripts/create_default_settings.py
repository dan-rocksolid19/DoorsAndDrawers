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
from core.models.door import RailDefaults


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
        right=Decimal('2.250')    # 2-1/4"
    )
    
    print(f"Created rail defaults: {rail_defaults}")
    return rail_defaults


def main():
    """Main function to create all default settings."""
    print("Creating default settings...")
    drawer_defaults = create_drawer_defaults()
    rail_defaults = create_rail_defaults()
    
    print("\nSummary:")
    print(f"Drawer Default Settings: ID={drawer_defaults.id}")
    print(f"Rail Defaults: ID={rail_defaults.id}")
    print("\nDefault settings creation completed successfully.")


if __name__ == "__main__":
    main() 