from ftplib import all_errors

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import OrderForm
from ..models import Order
from django.http import HttpResponse, JsonResponse
from ..models.customer import Customer
from ..models.door import DoorLineItem, RailDefaults
from django.db import transaction
from decimal import Decimal
from django.template.loader import render_to_string
from weasyprint import HTML
from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def orders(request):
    order_list = Order.confirmed.all().select_related('customer')
    page = request.GET.get('page', 1)
    
    # Paginate results
    paginator = Paginator(order_list, 10)  # 10 orders per page
    
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    return render(request, 'order/orders.html', {
        'orders': orders,
        'paginator': paginator,
        'min_id': '',
        'max_id': '',
        'start_date': '',
        'end_date': '',
        'customer_search': '',
        'title': 'Orders'
    })

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
                            quantity = int(item['quantity'])
                            custom_price = item.get('custom_price', False)
                            
                            # Only use the stored price_per_unit if custom_price is True
                            price_per_unit = Decimal(item['price_per_unit']) if custom_price else Decimal('0.00')

                            # Create door line item using values from the form/session
                            door_item = DoorLineItem(
                                order=order,
                                wood_stock_id=item['wood_stock']['id'],
                                edge_profile_id=item['edge_profile']['id'],
                                panel_rise_id=item['panel_rise']['id'],
                                style_id=item['style']['id'],
                                width=width,
                                height=height,
                                quantity=quantity,
                                price_per_unit=price_per_unit,
                                # Use rail dimensions directly from session data
                                rail_top=Decimal(item['rail_top']),
                                rail_bottom=Decimal(item['rail_bottom']),
                                rail_left=Decimal(item['rail_left']),
                                rail_right=Decimal(item['rail_right']),
                                # Save custom price flag if it exists
                                custom_price=custom_price
                            )
                            door_item.save()
                        # Handle other item types here (drawers, etc.) as needed
                        elif item.get('type') == 'drawer':
                            # Get drawer components
                            width = Decimal(item['width'])
                            height = Decimal(item['height'])
                            depth = Decimal(item['depth'])
                            quantity = int(item['quantity'])
                            custom_price = item.get('custom_price', False)
                            
                            # Only use the stored price_per_unit if custom_price is True
                            price_per_unit = Decimal(item['price_per_unit']) if custom_price else Decimal('0.00')

                            # Import here to avoid circular imports
                            from ..models.drawer import DrawerLineItem
                            
                            # Create drawer line item using values from the form/session
                            drawer_item = DrawerLineItem(
                                order=order,
                                wood_stock_id=item['wood_stock']['id'],
                                edge_type_id=item['edge_type']['id'],
                                bottom_id=item['bottom']['id'],
                                width=width,
                                height=height,
                                depth=depth,
                                quantity=quantity,
                                price_per_unit=price_per_unit,
                                undermount=item.get('undermount', False),
                                finishing=item.get('finishing', False),
                                # Save custom price flag if it exists
                                custom_price=custom_price
                            )
                            drawer_item.save()
                        # Handle generic items
                        elif item.get('type') == 'other':
                            # Get item details
                            name = item.get('name')
                            quantity = int(item.get('quantity'))
                            custom_price = item.get('custom_price', False)
                            
                            # Only use the stored price_per_unit if custom_price is True
                            price_per_unit = Decimal(item.get('price_per_unit'))
                            
                            # Import here to avoid circular imports
                            from ..models.line_item import GenericLineItem
                            
                            # Create generic line item
                            generic_item = GenericLineItem(
                                order=order,
                                name=name,
                                quantity=quantity,
                                price_per_unit=price_per_unit,
                                # Save custom price flag if it exists
                                custom_price=custom_price
                            )
                            generic_item.save()
                    
                    # Calculate and save order totals
                    order.calculate_totals()
                    order.save()
                    
                    # Clear session data after successful save
                    if 'current_order' in request.session:
                        del request.session['current_order']
                        request.session.modified = True
                    
                    messages.success(request, 'Order created successfully!')
                    return redirect('order_detail', order_id=order.id)
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

def order_search(request):
    min_id = request.GET.get('min_id', '')
    max_id = request.GET.get('max_id', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    customer_query = request.GET.get('customer_search', '').strip()
    page = request.GET.get('page', 1)
    
    # Start with all orders
    orders_query = Order.confirmed.all().select_related('customer')
    
    # Apply filters if provided
    if min_id and min_id.isdigit():
        orders_query = orders_query.filter(id__gte=int(min_id))
    
    if max_id and max_id.isdigit():
        orders_query = orders_query.filter(id__lte=int(max_id))
    
    # Apply date filters if provided
    try:
        if start_date:
            orders_query = orders_query.filter(order_date__gte=start_date)
        
        if end_date:
            orders_query = orders_query.filter(order_date__lte=end_date)
    except ValueError:
        # If date format is invalid, return all orders
        pass
    
    # Apply customer filter if provided
    if customer_query:
        orders_query = orders_query.filter(customer__company_name__icontains=customer_query)
    
    # Order by descending order date (newest first)
    orders_query = orders_query.order_by('-order_date')
    
    # Paginate results
    paginator = Paginator(orders_query, 10)  # 10 orders per page
    
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    # Return the paginated results
    return render(request, 'order/partials/order_results.html', {
        'orders': orders,
        'min_id': min_id,
        'max_id': max_id,
        'start_date': start_date,
        'end_date': end_date,
        'customer_search': customer_query,
        'paginator': paginator
    })

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