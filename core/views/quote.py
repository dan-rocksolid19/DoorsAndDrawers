from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import QuoteForm
from ..models import Order
from ..models.door import DoorLineItem, RailDefaults
from django.db import transaction
from decimal import Decimal
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def quotes(request):
    quote_list = Order.quotes.all().select_related('customer')
    page = request.GET.get('page', 1)
    
    # Paginate results
    paginator = Paginator(quote_list, 10)  # 10 quotes per page
    
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)
    
    return render(request, 'quote/quotes.html', {
        'quotes': quotes,
        'paginator': paginator,
        'min_id': '',
        'max_id': '',
        'start_date': '',
        'end_date': '',
        'customer_search': '',
        'title': 'Quotes'
    })

def quote_detail(request, quote_id):
    quote = get_object_or_404(Order.quotes, id=quote_id)
    
    # Get all door line items related to this quote
    door_items = DoorLineItem.objects.filter(order=quote).select_related(
        'wood_stock', 'edge_profile', 'panel_rise', 'style'
    )
    
    # Get all drawer line items related to this quote
    drawer_items = quote.drawer_items.all().select_related(
        'wood_stock', 'edge_type', 'bottom'
    )
    
    # Get all generic line items related to this quote
    generic_items = quote.generic_items.all()
    
    return render(request, 'quote/quote_detail.html', {
        'quote': quote,
        'door_items': door_items,
        'drawer_items': drawer_items,
        'generic_items': generic_items,
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
                    
                    # Get rail defaults (use the first one available)
                    rail_defaults = RailDefaults.objects.first()
                    
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

                            # Create door line item with rail default values
                            door_item = DoorLineItem(
                                order=quote,
                                wood_stock_id=item['wood_stock']['id'],
                                edge_profile_id=item['edge_profile']['id'],
                                panel_rise_id=item['panel_rise']['id'],
                                style_id=item['style']['id'],
                                width=width,
                                height=height,
                                quantity=quantity,
                                price_per_unit=price_per_unit,
                                # Add rail default values
                                rail_top=rail_defaults.top if rail_defaults else Decimal('2.50'),
                                rail_bottom=rail_defaults.bottom if rail_defaults else Decimal('2.50'),
                                rail_left=rail_defaults.left if rail_defaults else Decimal('2.50'),
                                rail_right=rail_defaults.right if rail_defaults else Decimal('2.50'),
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
                                order=quote,
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
                                order=quote,
                                name=name,
                                quantity=quantity,
                                price_per_unit=price_per_unit,
                                # Save custom price flag if it exists
                                custom_price=custom_price
                            )
                            generic_item.save()
                    
                    # Calculate and save quote totals
                    quote.calculate_totals()
                    quote.save()
                    
                    # Clear session data after successful save
                    if 'current_order' in request.session:
                        del request.session['current_order']
                        request.session.modified = True
                    
                    messages.success(request, 'Quote created successfully!')
                    return redirect('quote_detail', quote_id=quote.id)
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

def delete_quote(request, quote_id):
    quote = get_object_or_404(Order.quotes, id=quote_id)
    if request.method == 'POST':
        quote.delete()
        messages.success(request, 'Quote deleted successfully!')
        return redirect('quotes')
    
    return render(request, 'quote/quote_confirm_delete.html', {
        'quote': quote,
        'title': f'Delete Quote {quote.order_number}'
    })

def convert_to_order(request, quote_id):
    quote = get_object_or_404(Order.quotes, id=quote_id)
    if request.method == 'POST':
        quote.is_quote = False
        quote.save()
        messages.success(request, 'Quote converted to order successfully!')
        return redirect('order_detail', order_id=quote.id)
    
    return render(request, 'quote/quote_convert_confirm.html', {
        'quote': quote,
        'title': f'Convert Quote {quote.order_number} to Order'
    })


def quote_search(request):
    min_id = request.GET.get('min_id', '')
    max_id = request.GET.get('max_id', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    customer_query = request.GET.get('customer_search', '').strip()
    page = request.GET.get('page', 1)

    # Start with all quotes
    quotes_query = Order.quotes.all().select_related('customer')

    # Apply filters if provided
    if min_id and min_id.isdigit():
        quotes_query = quotes_query.filter(id__gte=int(min_id))

    if max_id and max_id.isdigit():
        quotes_query = quotes_query.filter(id__lte=int(max_id))
        
    # Apply date filters if provided
    try:
        if start_date:
            quotes_query = quotes_query.filter(order_date__gte=start_date)
        
        if end_date:
            quotes_query = quotes_query.filter(order_date__lte=end_date)
    except ValueError:
        # If date format is invalid, return all quotes
        pass
    
    # Apply customer filter if provided
    if customer_query:
        quotes_query = quotes_query.filter(customer__company_name__icontains=customer_query)

    # Order by descending order date (newest first)
    quotes_query = quotes_query.order_by('-order_date')
    
    # Paginate results
    paginator = Paginator(quotes_query, 10)  # 10 quotes per page
    
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)

    # Return the paginated results
    return render(request, 'quote/partials/quote_results.html', {
        'quotes': quotes,
        'min_id': min_id,
        'max_id': max_id,
        'start_date': start_date,
        'end_date': end_date,
        'customer_search': customer_query,
        'paginator': paginator
    })


def generate_quote_pdf(request, quote_id):
    """Generate a PDF version of the quote for printing."""
    quote = get_object_or_404(Order.quotes, id=quote_id)
    
    # Get all door line items related to this quote
    door_items = DoorLineItem.objects.filter(order=quote).select_related(
        'wood_stock', 'edge_profile', 'panel_rise', 'style'
    )
    
    # Get all drawer line items related to this quote
    drawer_items = quote.drawer_items.all().select_related(
        'wood_stock', 'edge_type', 'bottom'
    )
    
    # Get all generic line items related to this quote
    generic_items = quote.generic_items.all()
    
    # Render the HTML template
    html_string = render_to_string('pdf/quote_pdf.html', {
        'quote': quote,
        'door_items': door_items,
        'drawer_items': drawer_items,
        'generic_items': generic_items
    })
    
    # Create a PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quote_{quote.order_number}.pdf"'
    
    # Generate PDF
    HTML(string=html_string).write_pdf(response)
    
    return response 