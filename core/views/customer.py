from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import CustomerForm, CustomerDoorDefaultsForm, CustomerDrawerDefaultsForm
from ..models import Customer
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..services.door_defaults_service import DoorDefaultsService

def customers(request):
    customer_list = Customer.objects.all().order_by('-id')
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    
    # Paginate results
    paginator = Paginator(customer_list, 10)  # 10 customers per page
    
    try:
        all_customers = paginator.page(page)
    except PageNotAnInteger:
        all_customers = paginator.page(1)
    except EmptyPage:
        all_customers = paginator.page(paginator.num_pages)
    
    return render(request, 'customer/customers.html', {
        'customers': all_customers,
        'search_query': search_query,
        'paginator': paginator,
        'title': 'Customers'
    })

def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
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
            return redirect('customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm()
    
    return render(request, 'customer/customer_form.html', {
        'form': form,
        'title': 'New Customer'
    })

def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customer/customer_form.html', {
        'form': form,
        'title': f'Edit Customer: {customer.company_name}',
        'is_edit': True
    })

def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
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
        all_customers = paginator.page(page)
    except PageNotAnInteger:
        all_customers = paginator.page(1)
    except EmptyPage:
        all_customers = paginator.page(paginator.num_pages)
    
    # Return the paginated results with the appropriate template
    return render(request, 'customer/partials/customer_results.html', {
        'customers': all_customers,
        'search_query': search_query,
        'paginator': paginator
    })

def customer_defaults(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    door_defaults_service = DoorDefaultsService()
    
    if request.method == 'POST':
        if 'door_form' in request.POST:
            door_form = CustomerDoorDefaultsForm(request.POST)
            drawer_form = CustomerDrawerDefaultsForm(initial=customer.get_drawer_defaults())
            
            if door_form.is_valid():
                # Use service to prepare data for storage
                door_data = door_defaults_service.prepare_defaults_for_storage(door_form.cleaned_data)
                
                # Update customer's door_defaults
                customer.door_defaults = door_data
                customer.save(update_fields=['door_defaults'])
                
                messages.success(request, "Door defaults updated successfully")
                return redirect('customer_defaults', customer_id=customer.id)
        else:
            door_form = CustomerDoorDefaultsForm(initial=door_defaults_service.apply_defaults_to_form(customer))
            drawer_form = CustomerDrawerDefaultsForm(request.POST)
            
            if drawer_form.is_valid():
                # Convert model instances to IDs for JSON serialization
                drawer_data = {}
                for key, value in drawer_form.cleaned_data.items():
                    if value is not None:
                        if hasattr(value, 'pk'):  # If it's a model instance
                            drawer_data[key] = value.pk
                        else:  # For boolean fields and other primitives
                            drawer_data[key] = value
                
                # Update customer's drawer_defaults
                customer.drawer_defaults = drawer_data
                customer.save(update_fields=['drawer_defaults'])
                messages.success(request, "Drawer defaults updated successfully")
                return redirect('customer_defaults', customer_id=customer.id)
    else:
        # For GET request, initialize the forms
        door_form = CustomerDoorDefaultsForm(initial=door_defaults_service.apply_defaults_to_form(customer))
        drawer_form = CustomerDrawerDefaultsForm(initial=customer.get_drawer_defaults())
    
    context = {
        'customer': customer,
        'door_form': door_form,
        'drawer_form': drawer_form,
        'title': f'Defaults for {customer.company_name.title()}',
        'global_rail_defaults': door_defaults_service.global_defaults
    }
    
    return render(request, 'customer/customer_defaults.html', context) 