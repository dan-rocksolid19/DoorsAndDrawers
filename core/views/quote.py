from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import QuoteForm
from ..models import Order
from ..models.door import DoorLineItem
from django.db import transaction
from decimal import Decimal

def quotes(request):
    quotes = Order.quotes.all().select_related('customer')
    return render(request, 'quote/quotes.html', {
        'quotes': quotes,
        'title': 'Quotes'
    })

def quote_detail(request, id):
    quote = get_object_or_404(Order.quotes, id=id)
    
    # Get all door line items related to this quote
    door_items = DoorLineItem.objects.filter(order=quote).select_related(
        'wood_stock', 'edge_profile', 'panel_rise', 'style'
    )
    
    # Calculate quote total
    quote_total = sum(item.total_price for item in door_items)
    
    return render(request, 'quote/quote_detail.html', {
        'quote': quote,
        'door_items': door_items,
        'quote_total': quote_total,
        'title': f'Quote {quote.order_number}'
    })

def create_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            # Check if there's order data in the session
            if 'current_order' not in request.session or not request.session['current_order'].get('items'):
                messages.error(request, 'No line items found. Please add items to your quote.')
                return render(request, 'quote/quote_form.html', {'form': form, 'title': 'Create Quote'})
                
            # Validate session data matches submitted form data
            session_customer = request.session['current_order'].get('customer')
            form_customer = form.cleaned_data.get('customer').id
            if str(session_customer) != str(form_customer):
                messages.error(request, 'Customer information mismatch. Please try again.')
                return render(request, 'quote/quote_form.html', {'form': form, 'title': 'Create Quote'})
            
            # Begin database transaction
            try:
                with transaction.atomic():
                    # Save the quote
                    quote = form.save()
                    
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
                                order=quote,
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
                    
                    # Calculate and save quote totals
                    quote.calculate_totals()
                    quote.save()
                    
                    # Clear session data after successful save
                    if 'current_order' in request.session:
                        del request.session['current_order']
                        request.session.modified = True
                    
                    messages.success(request, 'Quote created successfully!')
                    return redirect('quote_detail', id=quote.id)
            except Exception as e:
                # Log the error for debugging (would implement proper logging in production)
                print(f"Error creating quote: {str(e)}")
                messages.error(request, f'Error creating quote: {str(e)}')
                return render(request, 'quote/quote_form.html', {'form': form, 'title': 'Create Quote'})
    else:
        form = QuoteForm()
    
    return render(request, 'quote/quote_form.html', {
        'form': form,
        'title': 'Create Quote'
    })

def delete_quote(request, id):
    quote = get_object_or_404(Order.quotes, id=id)
    if request.method == 'POST':
        quote.delete()
        messages.success(request, 'Quote deleted successfully!')
        return redirect('quotes')
    
    return render(request, 'quote/quote_confirm_delete.html', {
        'quote': quote,
        'title': f'Delete Quote {quote.order_number}'
    })

def convert_to_order(request, id):
    quote = get_object_or_404(Order.quotes, id=id)
    if request.method == 'POST':
        quote.is_quote = False
        quote.save()
        messages.success(request, 'Quote converted to order successfully!')
        return redirect('order_detail', id=quote.id)
    
    return render(request, 'quote/quote_convert_confirm.html', {
        'quote': quote,
        'title': f'Convert Quote {quote.order_number} to Order'
    }) 