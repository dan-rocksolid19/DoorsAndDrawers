from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import CustomerForm
from ..models import Customer

def customers(request):
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'customer/customers.html', {
        'customers': customers,
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