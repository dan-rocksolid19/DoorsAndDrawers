from faker import Faker
import random
import os
import django
from decimal import Decimal
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doors_and_drawers.settings')
django.setup()

# Now import the models
from core.models import Customer, CustomerDefaults
from core.utils import get_us_states

fake = Faker()

def generate_customers(n=10, create_defaults=True):
    """
    Generate n fake customers and optionally create defaults for each.
    
    Args:
        n (int): Number of customers to generate
        create_defaults (bool): Whether to create customer defaults
        
    Returns:
        list: List of created Customer instances
    """
    print(f"Generating {n} fake customers...")
    
    # Get state choices for random selection
    state_choices = get_us_states()
    state_codes = [code for code, name in state_choices]
    
    created_customers = []
    
    with transaction.atomic():
        for i in range(n):
            # Generate a random company name
            company_type = random.choice(['Woodworks', 'Cabinets', 'Furniture', 'Interiors', 'Carpentry', 'Designs', 'Home', 'Kitchen', 'Custom'])
            company_name = f"{fake.last_name()} {company_type}"
            
            # Create the customer
            customer = Customer(
                company_name=company_name,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                address_line1=fake.street_address(),
                address_line2="" if random.random() < 0.7 else fake.secondary_address(),
                city=fake.city(),
                state=random.choice(state_codes),
                zip_code=fake.zipcode()[:5],
                phone="".join([str(random.randint(0, 9)) for _ in range(10)]),
                fax="".join([str(random.randint(0, 9)) for _ in range(10)]),
                notes=fake.paragraph(nb_sentences=3) if random.random() < 0.5 else ""
            )
            customer.save()
            created_customers.append(customer)
            
            print(f"Created customer: {customer}")
            
            # Create customer defaults if requested
            if create_defaults:
                discount_type = random.choice(['PERCENT', 'FIXED'])
                discount_value = Decimal(str(random.randint(0, 15))) if discount_type == 'PERCENT' else Decimal(str(random.randint(0, 200)))
                
                surcharge_type = random.choice(['PERCENT', 'FIXED'])
                surcharge_value = Decimal(str(random.randint(0, 10))) if surcharge_type == 'PERCENT' else Decimal(str(random.randint(0, 100)))
                
                shipping_type = random.choice(['PERCENT', 'FIXED'])
                shipping_value = Decimal(str(random.randint(0, 15))) if shipping_type == 'PERCENT' else Decimal(str(random.randint(0, 100)))
                
                defaults = CustomerDefaults(
                    customer=customer,
                    discount_type=discount_type,
                    discount_value=discount_value,
                    surcharge_type=surcharge_type,
                    surcharge_value=surcharge_value,
                    shipping_type=shipping_type,
                    shipping_value=shipping_value
                )
                defaults.save()
                print(f"Created defaults for: {customer}")
    
    print(f"Successfully generated {len(created_customers)} customers.")
    return created_customers

# Example usage:
# python manage.py shell
# from scripts.generate_customers import generate_customers
# generate_customers(10) 