#!/usr/bin/env python
"""
Script to add drawer line items to existing orders and quotes.
Run with: python manage.py runscript add_drawer_items
"""
import random
import argparse
from decimal import Decimal
from django.utils import timezone
from core.models import (
    Order, 
    DrawerWoodStock, 
    DrawerEdgeType, 
    DrawerBottomSize, 
    DrawerLineItem
)

def run(*args):
    parser = argparse.ArgumentParser(description='Add drawer items to orders and quotes.')
    parser.add_argument('--orders', nargs='*', type=int, help='Order IDs to add drawers to')
    parser.add_argument('--quotes', nargs='*', type=int, help='Quote IDs to add drawers to')
    parser.add_argument('--all', action='store_true', help='Add drawers to recent orders and quotes')
    parser.add_argument('--count', type=int, default=3, help='Number of recent orders/quotes to process if using --all')
    
    # If no args provided, use some defaults
    if not args:
        args = ['--all']
    
    # Parse the args
    parsed_args = parser.parse_args(args)
    
    # Find the orders and quotes to process
    records_to_process = []
    
    # If specific order IDs were provided
    if parsed_args.orders:
        orders = Order.confirmed.filter(pk__in=parsed_args.orders)
        records_to_process.extend(orders)
        print(f"Found {orders.count()} specific orders")
    
    # If specific quote IDs were provided
    if parsed_args.quotes:
        quotes = Order.quotes.filter(pk__in=parsed_args.quotes)
        records_to_process.extend(quotes)
        print(f"Found {quotes.count()} specific quotes")
    
    # If --all flag was set, add recent orders and quotes
    if parsed_args.all or not records_to_process:
        count = parsed_args.count
        recent_orders = Order.confirmed.all().order_by('-order_date')[:count]
        recent_quotes = Order.quotes.all().order_by('-order_date')[:count]
        
        records_to_process.extend(recent_orders)
        records_to_process.extend(recent_quotes)
        
        print(f"Found {recent_orders.count()} recent orders and {recent_quotes.count()} recent quotes")
    
    if not records_to_process:
        print("No orders or quotes found to process. Please check your database.")
        return

    print(f"Will process {len(records_to_process)} records (orders & quotes)")
    
    # Get or create the required related objects
    wood_stock_types = ensure_wood_stock_exists()
    edge_types = ensure_edge_types_exist()
    bottom_sizes = ensure_bottom_sizes_exist()

    # Sample drawer dimensions (width, height, depth)
    sample_drawers = [
        {"width": 24, "height": 6, "depth": 21},
        {"width": 30, "height": 8, "depth": 21},
        {"width": 15, "height": 4, "depth": 18},
        {"width": 18, "height": 5, "depth": 20},
        {"width": 36, "height": 10, "depth": 22},
    ]

    # Add drawers to each record
    created_drawers = []
    for record in records_to_process:
        record_type = "Quote" if record.is_quote else "Order"
        print(f"\nAdding drawers to {record_type} {record.order_number}...")
        
        # Add 2-4 drawers to each record
        num_drawers = random.randint(2, 4)
        for i in range(num_drawers):
            # Pick random drawer dimensions and components
            drawer_dims = random.choice(sample_drawers)
            wood_stock = random.choice(wood_stock_types)
            edge_type = random.choice(edge_types)
            bottom_size = random.choice(bottom_sizes)
            
            price_per_unit = wood_stock.price + bottom_size.price
            drawer = DrawerLineItem.objects.create(
                order=record,
                type='drawer',
                price_per_unit=price_per_unit,
                quantity=random.randint(1, 3),  # Add multiple quantities sometimes
                width=Decimal(str(drawer_dims["width"])),
                height=Decimal(str(drawer_dims["height"])),
                depth=Decimal(str(drawer_dims["depth"])),
                wood_stock=wood_stock,
                edge_type=edge_type,
                bottom=bottom_size,
                undermount=random.choice([True, False]),
                finishing=random.choice([True, False])
            )
            created_drawers.append(drawer)
            print(f"  Created drawer: {drawer} (Price: ${drawer.total_price})")
        
        # Recalculate record totals
        record.calculate_totals()
        record.save()
        print(f"  Updated {record_type.lower()} total: ${record.total}")

    print(f"\nCreated {len(created_drawers)} drawer line items across {len(records_to_process)} records.")

    # Show summary of a record with our new API
    if records_to_process:
        record = records_to_process[0]
        record_type = "Quote" if record.is_quote else "Order"
        print(f"\nFor {record_type} {record.order_number}:")
        print(f"Door items count: {record.door_items.count()}")
        print(f"Drawer items count: {record.drawer_items.count()}")
        print(f"All line items count: {len(record.line_items)}")
        
        print("\nSummary:", record.get_item_types_summary())
        
        print("\nAccessing individual items:")
        if record.line_items:
            for i, item in enumerate(record.line_items[:3]):  # Show first 3 items
                item_type = "Door" if hasattr(item, "style") else "Drawer"
                print(f"Item {i+1}: {item_type} - {item}")

def ensure_wood_stock_exists():
    """Ensure we have drawer wood stock options"""
    wood_types = [
        {"name": "Maple", "price": Decimal("5.50")},
        {"name": "Oak", "price": Decimal("4.75")},
        {"name": "Cherry", "price": Decimal("7.25")},
        {"name": "Walnut", "price": Decimal("8.50")},
    ]
    
    wood_stocks = []
    for wood in wood_types:
        wood_stock, created = DrawerWoodStock.objects.get_or_create(
            name=wood["name"],
            defaults={"price": wood["price"]}
        )
        wood_stocks.append(wood_stock)
        if created:
            print(f"Created wood stock: {wood_stock.name}")
    
    return wood_stocks

def ensure_edge_types_exist():
    """Ensure we have drawer edge types"""
    edge_names = ["Standard Edge", "Round Edge", "Bevel Edge", "Decorative Edge"]
    
    edge_types = []
    for name in edge_names:
        edge_type, created = DrawerEdgeType.objects.get_or_create(name=name)
        edge_types.append(edge_type)
        if created:
            print(f"Created edge type: {edge_type.name}")
    
    return edge_types

def ensure_bottom_sizes_exist():
    """Ensure we have drawer bottom sizes"""
    bottom_types = [
        {"name": "1/4\" Standard", "thickness": Decimal("0.250"), "price": Decimal("2.50")},
        {"name": "3/8\" Medium", "thickness": Decimal("0.375"), "price": Decimal("3.75")},
        {"name": "1/2\" Heavy", "thickness": Decimal("0.500"), "price": Decimal("5.00")},
    ]
    
    bottom_sizes = []
    for bottom in bottom_types:
        bottom_size, created = DrawerBottomSize.objects.get_or_create(
            name=bottom["name"],
            defaults={
                "thickness": bottom["thickness"],
                "price": bottom["price"]
            }
        )
        bottom_sizes.append(bottom_size)
        if created:
            print(f"Created bottom size: {bottom_size.name}")
    
    return bottom_sizes

if __name__ == "__main__":
    print("This script should be run using 'python manage.py runscript add_drawer_items'")
    print("You can also specify arguments for more control:")
    print("python manage.py runscript add_drawer_items --script-args --orders 1 2 3")
    print("python manage.py runscript add_drawer_items --script-args --quotes 1 2 3")
    print("python manage.py runscript add_drawer_items --script-args --all --count 5") 