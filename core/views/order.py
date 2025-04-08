from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import OrderForm
from ..models import Order
from django.http import HttpResponse, JsonResponse
from ..models.customer import Customer

def orders(request):
    orders = Order.confirmed.all().select_related('customer')
    return render(request, 'order/orders.html', {
        'orders': orders,
        'title': 'Orders'
    })

def order_detail(request, id):
    order = get_object_or_404(Order.confirmed, id=id)
    return render(request, 'order/order_detail.html', {
        'order': order,
        'title': f'Order {order.order_number}'
    })

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(
                request, 
                'Order created successfully!'
                )
            return redirect('order_detail', id=order.id)
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
        
        response_data = {
            'addresses': {
                'address1': customer.address_line1 or '',
                'address2': customer.address_line2 or ''
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