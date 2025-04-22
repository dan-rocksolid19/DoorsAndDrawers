from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import QuoteForm
from ..models import Order
from ..models.door import DoorLineItem
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from ..services.order_service import OrderService
from .common import handle_entity_search, handle_entity_list

def quotes(request):
    """List all quotes with pagination."""
    # Use the common list handler with quote-specific parameters
    return handle_entity_list(
        request,
        Order.quotes.all().select_related('customer'),
        'quote/quotes.html',
        'quotes',
        'Quotes'
    )

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
            # Use OrderService to create the quote
            success, quote, error = OrderService.create_from_session(
                form.cleaned_data,
                request.session.get('current_order', {}),
                is_quote=True
            )
            
            if success:
                # Clear session data
                if 'current_order' in request.session:
                    del request.session['current_order']
                    request.session.modified = True
                
                messages.success(request, 'Quote created successfully!')
                return redirect('quote_detail', quote_id=quote.id)
            else:
                messages.error(request, error)
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
    """Search and filter quotes based on criteria."""
    # Use the common search handler with quote-specific parameters
    return handle_entity_search(
        request,
        Order.quotes.all().select_related('customer'),
        'quote/partials/quote_results.html',
        'quotes'
    )

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