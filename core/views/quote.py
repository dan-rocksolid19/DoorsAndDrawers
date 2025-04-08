from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import QuoteForm
from ..models import Order

def quotes(request):
    quotes = Order.quotes.all().select_related('customer')
    return render(request, 'quote/quotes.html', {
        'quotes': quotes,
        'title': 'Quotes'
    })

def quote_detail(request, id):
    quote = get_object_or_404(Order.quotes, id=id)
    return render(request, 'quote/quote_detail.html', {
        'quote': quote,
        'title': f'Quote {quote.order_number}'
    })

def create_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save()
            messages.success(request, 'Quote created successfully!')
            return redirect('quote_detail', id=quote.id)
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