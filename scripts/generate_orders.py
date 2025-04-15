from faker import Faker
import random
import os
import django
from decimal import Decimal
from django.db import transaction
from datetime import timedelta, date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doors_and_drawers.settings')
django.setup()

# Now import the models
from core.models import Customer, Order, DoorLineItem, WoodStock, EdgeProfile, PanelRise, Style, RailDefaults
from core.models.drawer import DrawerLineItem, DrawerWoodStock, DrawerEdgeType, DrawerBottomSize
from django.utils import timezone

fake = Faker()

def generate_orders(n=5, is_quote=False, max_items_per_order=5, min_items_per_order=1):
    """
    Generate n fake orders with door and drawer line items.
    
    Args:
        n (int): Number of orders to generate
        is_quote (bool): Whether to create quotes (True) or confirmed orders (False)
        max_items_per_order (int): Maximum number of line items per order
        min_items_per_order (int): Minimum number of line items per order
        
    Returns:
        list: List of created Order instances
    """
    print(f"Generating {n} fake {'quotes' if is_quote else 'orders'}...")
    
    # Get customers (need at least one customer in the database)
    customers = list(Customer.objects.all())
    if not customers:
        print("No customers found in database. Please create customers first.")
        return []
    
    # Get required model instances for creating door items
    wood_stocks = list(WoodStock.objects.all())
    edge_profiles = list(EdgeProfile.objects.all())
    panel_rises = list(PanelRise.objects.all())
    styles = list(Style.objects.all())
    rail_defaults = RailDefaults.objects.first()
    
    # Get required model instances for creating drawer items
    drawer_wood_stocks = list(DrawerWoodStock.objects.all())
    drawer_edge_types = list(DrawerEdgeType.objects.all())
    drawer_bottoms = list(DrawerBottomSize.objects.all())
    
    # Check if we have the required data for doors
    if not all([wood_stocks, edge_profiles, panel_rises, styles]):
        print("Missing required data to create door items. Check your database setup.")
        return []
    
    # Check if we have the required data for drawers
    if not all([drawer_wood_stocks, drawer_edge_types, drawer_bottoms]):
        print("Missing required data to create drawer items. Check your database setup.")
        print("Will generate orders with doors only.")
    
    # Set default rail values
    default_rail_values = {
        'rail_top': Decimal('2.50'),
        'rail_bottom': Decimal('2.50'),
        'rail_left': Decimal('2.50'),
        'rail_right': Decimal('2.50')
    }
    
    if rail_defaults:
        default_rail_values = {
            'rail_top': rail_defaults.top,
            'rail_bottom': rail_defaults.bottom,
            'rail_left': rail_defaults.left,
            'rail_right': rail_defaults.right
        }
    
    created_orders = []
    
    with transaction.atomic():
        for i in range(n):
            # Pick a random customer
            customer = random.choice(customers)
            
            # Random date within last year
            order_date = timezone.now().date() - timedelta(days=random.randint(0, 365))
            
            # Create the order
            order = Order(
                customer=customer,
                is_quote=is_quote,
                billing_address1=customer.address_line1,
                billing_address2=customer.address_line2,
                order_date=order_date,
                notes=fake.paragraph(nb_sentences=2) if random.random() < 0.3 else ""
            )
            order.save()
            created_orders.append(order)
            
            # Generate random number of line items
            num_items = random.randint(min_items_per_order, max_items_per_order)
            
            for j in range(num_items):
                # Randomly choose between door and drawer (if drawer data is available)
                if all([drawer_wood_stocks, drawer_edge_types, drawer_bottoms]) and random.random() < 0.4:
                    # Create a drawer item
                    drawer_wood_stock = random.choice(drawer_wood_stocks)
                    drawer_edge_type = random.choice(drawer_edge_types)
                    drawer_bottom = random.choice(drawer_bottoms)
                    
                    # Generate random dimensions (in inches)
                    width = Decimal(str(random.randint(12, 36)))
                    height = Decimal(str(random.randint(4, 12)))
                    depth = Decimal(str(random.randint(16, 24)))
                    quantity = random.randint(1, 10)
                    
                    # Randomly assign options
                    undermount = random.random() < 0.7
                    finishing = random.random() < 0.5
                    
                    # Calculate a simple price
                    price_per_unit = drawer_wood_stock.price + drawer_bottom.price + Decimal('35.00')
                    if undermount:
                        price_per_unit += Decimal('15.00')
                    if finishing:
                        price_per_unit += Decimal('10.00')
                    
                    # Create drawer line item
                    drawer_item = DrawerLineItem(
                        order=order,
                        wood_stock=drawer_wood_stock,
                        edge_type=drawer_edge_type,
                        bottom=drawer_bottom,
                        width=width,
                        height=height,
                        depth=depth,
                        quantity=quantity,
                        price_per_unit=price_per_unit,
                        undermount=undermount,
                        finishing=finishing,
                        type='drawer'
                    )
                    drawer_item.save()
                    print(f"Added drawer item to {order}: {width}\"x{height}\"x{depth}\" {drawer_wood_stock.name}")
                else:
                    # Create a door item
                    wood_stock = random.choice(wood_stocks)
                    edge_profile = random.choice(edge_profiles)
                    panel_rise = random.choice(panel_rises)
                    style = random.choice(styles)
                    
                    # Generate random dimensions (in inches)
                    width = Decimal(str(random.randint(12, 36)))
                    height = Decimal(str(random.randint(12, 48)))
                    quantity = random.randint(1, 10)
                    
                    # Calculate price (simplified version of the actual pricing logic)
                    base_price = style.price
                    
                    # Determine woodstock price based on panel type
                    if style.panel_type.use_flat_panel_price:
                        woodstock_price = wood_stock.flat_panel_price
                    else:
                        woodstock_price = wood_stock.raised_panel_price
                    
                    # Calculate price per unit
                    price_per_unit = base_price + (woodstock_price * 2)
                    
                    # Create door line item
                    door_item = DoorLineItem(
                        order=order,
                        wood_stock=wood_stock,
                        edge_profile=edge_profile,
                        panel_rise=panel_rise,
                        style=style,
                        width=width,
                        height=height,
                        quantity=quantity,
                        price_per_unit=price_per_unit,
                        type='door',
                        **default_rail_values
                    )
                    door_item.save()
                    print(f"Added door item to {order}: {width}\"x{height}\" {wood_stock.name} {style.name}")
            
            # Calculate order totals
            try:
                order.calculate_totals()
                order.save()
                door_count = order.door_items.count()
                drawer_count = order.drawer_items.count()
                print(f"Created {'Quote' if is_quote else 'Order'} #{order.order_number} for {customer.company_name} with {door_count} doors and {drawer_count} drawers. Total: ${order.total}")
            except Exception as e:
                print(f"Error calculating totals for {order}: {e}")
                # Set default value if calculations fail
                order.total = sum(item.total_price for item in order.line_items)
                order.save()
    
    return created_orders

def generate_quotes_and_orders(num_quotes=5, num_orders=5):
    """
    Generate both quotes and orders.
    
    Args:
        num_quotes (int): Number of quotes to generate
        num_orders (int): Number of orders to generate
    """
    quotes = generate_orders(num_quotes, is_quote=True)
    orders = generate_orders(num_orders, is_quote=False)
    
    return {
        'quotes': quotes,
        'orders': orders
    }

# Example usage:
# python manage.py shell
# from scripts.generate_orders import generate_orders, generate_quotes_and_orders
# 
# # Generate 5 orders
# generate_orders(5, is_quote=False)
# 
# # Generate 3 quotes
# generate_orders(3, is_quote=True)
# 
# # Generate both quotes and orders
# generate_quotes_and_orders(4, 6) 