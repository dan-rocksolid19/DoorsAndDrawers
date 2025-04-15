from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import CustomerForm
from ..models import Customer
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def customers(request):
    customer_list = Customer.objects.all().order_by('-id')
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    
    # Paginate results
    paginator = Paginator(customer_list, 10)  # 10 customers per page
    
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
    
    return render(request, 'customer/customers.html', {
        'customers': customers,
        'search_query': search_query,
        'paginator': paginator,
        'title': 'Customers'
    })

def customer_detail(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, 'customer/customer_detail.html', {
        'customer': customer,
        'title': f'Customer: {customer.company_name}'
    })

def new_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(
                request, 
                f'Customer {customer.company_name} was successfully created!'
            )
            return redirect('customers')
    else:
        form = CustomerForm()
    
    return render(request, 'customer/customer_form.html', {
        'form': form,
        'title': 'New Customer'
    })

def edit_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_detail', id=customer.id)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customer/customer_form.html', {
        'form': form,
        'title': f'Edit Customer: {customer.company_name}',
        'is_edit': True
    })

def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customers')
    
    return render(request, 'customer/customer_confirm_delete.html', {
        'customer': customer,
        'title': f'Delete Customer: {customer.company_name}'
    })

def customer_search(request):
    search_query = request.GET.get('search', '').strip().lower()
    page = request.GET.get('page', 1)
    
    if not search_query:
        # If no search query, return all customers
        customer_list = Customer.objects.all().order_by('-id')
    else:
        # Search across multiple fields
        customer_list = Customer.objects.filter(
            models.Q(company_name__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(city__icontains=search_query) |
            models.Q(phone__icontains=search_query)
        ).order_by('-id')
    
    # Paginate results
    paginator = Paginator(customer_list, 10)  # 10 customers per page
    
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
    
    # Return the paginated results with the appropriate template
    return render(request, 'customer/partials/customer_results.html', {
        'customers': customers,
        'search_query': search_query,
        'paginator': paginator
    }) 