from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import OrderForm
from ..models import Order
from django.http import HttpResponse, JsonResponse
from ..models.customer import Customer
from ..models.door import DoorLineItem
from django.template.loader import render_to_string
from weasyprint import HTML
from itertools import chain
from ..services.order_service import OrderService
from .common import handle_entity_search, handle_entity_list

def orders(request):
    """List all confirmed orders with pagination."""
    # Use the common list handler with order-specific parameters
    return handle_entity_list(
        request,
        Order.confirmed.all().select_related('customer'),
        'order/orders.html',
        'orders',
        'Orders'
    )

def order_detail(request, order_id):
    order = get_object_or_404(Order.confirmed, id=order_id)
    
    # Get all door line items related to this order
    door_items = DoorLineItem.objects.filter(order=order).select_related(
        'wood_stock', 'edge_profile', 'panel_rise', 'style'
    )
    
    # Get all drawer line items related to this order
    drawer_items = order.drawer_items.all().select_related(
        'wood_stock', 'edge_type', 'bottom'
    )
    
    # Get all generic line items related to this order
    generic_items = order.generic_items.all()
    
    return render(request, 'order/order_detail.html', {
        'order': order,
        'door_items': door_items,
        'drawer_items': drawer_items,
        'generic_items': generic_items,
        'title': f'Order {order.order_number}'
    })

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Check if there are items in the order
            session_data = request.session.get('current_order', {})
            items = session_data.get('items', [])
            
            if not items:
                messages.error(request, "You need to add at least one item to create an order.")
                return render(request, 'order/order_form.html', {'form': form, 'title': 'Create Order'}, status=422)
            
            # Check if a customer is associated with the order
            if 'customer' not in session_data:
                messages.error(request, "Please select a customer for this order.")
                return render(request, 'order/order_form.html', {'form': form, 'title': 'Create Order'}, status=422)
            
            # Use OrderService to create the order
            success, order, error = OrderService.create_from_session(
                form.cleaned_data,
                session_data,
                is_quote=False
            )
            
            if success:
                # Clear session data
                if 'current_order' in request.session:
                    del request.session['current_order']
                    request.session.modified = True
                
                messages.success(request, 'Order created successfully!')
                return redirect('order_detail', order_id=order.id)
            else:
                # Provide more specific error messages based on the error type
                if "Data integrity error" in error:
                    messages.error(request, "There was a problem with the data in your order. Please check all fields and try again.")
                elif "Database error" in error:
                    messages.error(request, "There was a database problem. Please try again later.")
                else:
                    messages.error(request, error)
                
                return render(request, 'order/order_form.html', {'form': form, 'title': 'Create Order'}, status=422)
        else:
            # Form validation failed, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{form[field].label}: {error}")
            
            # Return the form with errors and 422 status code
            return render(request, 'order/order_form.html', {'form': form, 'title': 'Create Order'}, status=422)
    else:
        # Clear session data when first accessing the page (GET request)
        if 'current_order' in request.session:
            del request.session['current_order']
            request.session.modified = True
            
        form = OrderForm()
    
    return render(request, 'order/order_form.html', {
        'form': form,
        'title': 'Create Order'
    })

def delete_order(request, order_id):
    order = get_object_or_404(Order.confirmed, id=order_id)
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
        
        # Preserve existing items when changing customers
        existing_items = []
        if 'current_order' in request.session and 'items' in request.session['current_order']:
            existing_items = request.session['current_order']['items']
            
        # Update order in session with new customer data but keep existing items
        request.session['current_order'] = {
            'customer': customer_id,
            'billing_address1': billing_address1,
            'billing_address2': billing_address2,
            'items': existing_items
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

def order_search(request):
    """Search and filter orders based on criteria."""
    # Use the common search handler with order-specific parameters
    return handle_entity_search(
        request,
        Order.confirmed.all().select_related('customer'),
        'order/partials/order_results.html',
        'orders'
    )

def remove_line_item(request, item_id):
    """
    Remove a line item from the current order
    Handles both database-persisted items and session-based items
    """
    if request.method == 'DELETE':
        # First, check if we're working with a session-based order
        if 'current_order' in request.session:
            # Handle session-based item deletion
            try:
                # In session, item_id is actually the index of the item in the array
                index = int(item_id)
                if 'items' in request.session['current_order'] and 0 <= index < len(request.session['current_order']['items']):
                    # Remove the item at the specified index
                    request.session['current_order']['items'].pop(index)
                    # Mark session as modified
                    request.session.modified = True
                    # Return the updated line items table
                    return render(request, 'door/line_items_table.html', {
                        'items': request.session['current_order']['items']
                    })
                else:
                    return HttpResponse("Item not found in session", status=404)
            except (ValueError, IndexError):
                return HttpResponse("Invalid item index", status=400)
        
        # If not using session, handle database-persisted items
        order_id = request.session.get('order_id')
        if not order_id:
            return HttpResponse("No active order", status=400)
        
        order = get_object_or_404(Order, id=order_id)
        
        # Find and remove the line item
        item_removed = False
        
        # Try to find and remove from door items
        if hasattr(order, 'door_items'):
            door_item = order.door_items.filter(id=item_id).first()
            if door_item:
                door_item.delete()
                item_removed = True
        
        # If not found in door items, try drawer items
        if not item_removed and hasattr(order, 'drawer_items'):
            drawer_item = order.drawer_items.filter(id=item_id).first()
            if drawer_item:
                drawer_item.delete()
                item_removed = True
        
        if not item_removed:
            return HttpResponse("Item not found", status=404)
        
        # Get all remaining items to refresh the list
        # Use the line_items property if it exists, otherwise combine manually
        if hasattr(order, 'line_items') and callable(getattr(order, 'line_items')):
            items = order.line_items
        else:
            door_items = list(order.door_items.all()) if hasattr(order, 'door_items') else []
            drawer_items = list(order.drawer_items.all()) if hasattr(order, 'drawer_items') else []
            items = list(chain(door_items, drawer_items))
        
        # Return the updated line items table
        return render(request, 'door/line_items_table.html', {'items': items})
    
    # If not DELETE request, redirect to order detail
    return redirect('order_detail')

def generate_order_pdf(request, order_id):
    """Generate a PDF version of the order for printing."""
    order = get_object_or_404(Order.objects.filter(is_quote=False), id=order_id)
    
    # Get all door line items related to this order
    door_items = DoorLineItem.objects.filter(order=order).select_related(
        'wood_stock', 'edge_profile', 'panel_rise', 'style'
    )
    
    # Get all drawer line items related to this order
    drawer_items = order.drawer_items.all().select_related(
        'wood_stock', 'edge_type', 'bottom'
    )
    
    # Get all generic line items related to this order
    generic_items = order.generic_items.all()
    
    # Render the HTML template
    html_string = render_to_string('pdf/order_pdf.html', {
        'order': order,
        'door_items': door_items,
        'drawer_items': drawer_items,
        'generic_items': generic_items
    })
    
    # Create a PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.order_number}.pdf"'
    
    # Generate PDF
    HTML(string=html_string).write_pdf(response)
    
    return response 