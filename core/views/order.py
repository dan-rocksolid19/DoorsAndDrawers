from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import OrderForm
from ..models import Order
from django.http import HttpResponse, JsonResponse
from ..models.customer import Customer
from ..models.door import DoorLineItem, WoodStock, EdgeProfile, PanelRise, Style
from django.db import transaction
from decimal import Decimal

def orders(request):
    orders = Order.confirmed.all().select_related('customer')
    return render(request, 'order/orders.html', {
        'orders': orders,
        'title': 'Orders'
    })

def order_detail(request, id):
    order = get_object_or_404(Order.confirmed, id=id)
    
    # Get all door line items related to this order
    door_items = DoorLineItem.objects.filter(order=order).select_related(
        'wood_stock', 'edge_profile', 'panel_rise', 'style'
    )
    
    # Calculate order total
    order_total = sum(item.total_price for item in door_items)
    
    return render(request, 'order/order_detail.html', {
        'order': order,
        'door_items': door_items,
        'order_total': order_total,
        'title': f'Order {order.order_number}'
    })

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Check if there's order data in the session
            if 'current_order' not in request.session or not request.session['current_order'].get('items'):
                messages.error(request, 'No line items found. Please add items to your order.')
                return render(request, 'order/order_form.html', {'form': form, 'title': 'Create Order'})
                
            # Validate session data matches submitted form data
            session_customer = request.session['current_order'].get('customer')
            form_customer = form.cleaned_data.get('customer').id
            if str(session_customer) != str(form_customer):
                messages.error(request, 'Customer information mismatch. Please try again.')
                return render(request, 'order/order_form.html', {'form': form, 'title': 'Create Order'})
            
            # Begin database transaction
            try:
                with transaction.atomic():
                    # Save the order
                    order = form.save()
                    
                    # Process line items from session
                    line_items = request.session['current_order'].get('items', [])
                    for item in line_items:
                        if item.get('type') == 'door':
                            # Get door components
                            width = Decimal(item['width'])
                            height = Decimal(item['height'])
                            
                            price_per_unit = Decimal(item['price_per_unit'])

                            # Create door line item
                            door_item = DoorLineItem(
                                order=order,
                                wood_stock_id=item['wood_stock']['id'],
                                edge_profile_id=item['edge_profile']['id'],
                                panel_rise_id=item['panel_rise']['id'],
                                style_id=item['style']['id'],
                                width=width,
                                height=height,
                                quantity=item['quantity'],
                                price_per_unit=price_per_unit,
                            )
                            door_item.save()
                        # Handle other item types here (drawers, etc.) as needed
                    
                    # Clear session data after successful save
                    if 'current_order' in request.session:
                        del request.session['current_order']
                        request.session.modified = True
                    
                    messages.success(request, 'Order created successfully!')
                    return redirect('order_detail', id=order.id)
            except Exception as e:
                # Log the error for debugging (would implement proper logging in production)
                print(f"Error creating order: {str(e)}")
                messages.error(request, f'Error creating order: {str(e)}')
                return render(request, 'order/order_form.html', {'form': form, 'title': 'Create Order'})
    else:
        form = OrderForm()
    
    return render(request, 'order/order_form.html', {
        'form': form,
        'title': 'Create Order'
    })

def delete_order(request, id):
    order = get_object_or_404(Order.confirmed, id=id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('orders')
    
    return render(request, 'order/order_confirm_delete.html', {
        'order': order,
        'title': f'Delete Order {order.order_number}'
    })

def get_customer_details(request):
    customer_id = request.GET.get('customer')
    if not customer_id:
        return JsonResponse({
            'addresses': {'address1': '', 'address2': ''},
            'defaults': {
                'discount_type': '',
                'discount_value': '',
                'surcharge_type': '',
                'surcharge_value': '',
                'shipping_type': '',
                'shipping_value': ''
            }
        })
    
    try:
        customer = Customer.objects.get(id=customer_id)
        defaults = customer.defaults if hasattr(customer, 'defaults') else None

        billing_address1 = customer.address_line1 or ''
        billing_address2 = customer.address_line2 or ''
        
        response_data = {
            'addresses': {
                'address1': billing_address1,
                'address2': billing_address2
            },
            'defaults': {
                'discount_type': defaults.discount_type if defaults else '',
                'discount_value': str(defaults.discount_value) if defaults else '',
                'surcharge_type': defaults.surcharge_type if defaults else '',
                'surcharge_value': str(defaults.surcharge_value) if defaults else '',
                'shipping_type': defaults.shipping_type if defaults else '',
                'shipping_value': str(defaults.shipping_value) if defaults else ''
            }
        }
        
        # Add order to session
        request.session['current_order'] = {
            'customer': customer_id,
            'billing_address1': billing_address1,
            'billing_address2': billing_address2,
            # 'order_date': order_date,
            'items': []
        }

        request.session.modified = True

        return JsonResponse(response_data)
    except (Customer.DoesNotExist, ValueError):
        return JsonResponse({
            'addresses': {'address1': '', 'address2': ''},
            'defaults': {
                'discount_type': '',
                'discount_value': '',
                'surcharge_type': '',
                'surcharge_value': '',
                'shipping_type': '',
                'shipping_value': ''
            }
        }) 