from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..forms import CustomerForm, CustomerDoorDefaultsForm, CustomerDrawerDefaultsForm
from ..models import Customer
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import Decimal, InvalidOperation

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
    
    # Get current door defaults
    door_defaults = customer.get_door_defaults()
    
    # Get current drawer defaults
    drawer_defaults = customer.get_drawer_defaults()
    
    # Get global rail defaults for comparison
    from ..models.door import RailDefaults
    global_rail_defaults = RailDefaults.objects.first()
    
    if request.method == 'POST':
        if 'door_form' in request.POST:
            door_form = CustomerDoorDefaultsForm(request.POST)
            drawer_form = CustomerDrawerDefaultsForm(initial=drawer_defaults)
            
            if door_form.is_valid():
                # Extract non-empty values that are explicitly overridden
                door_data = {}
                
                # For model choices, only include if selected and not None
                for field in ['wood_stock', 'edge_profile', 'panel_rise', 'style']:
                    if door_form.cleaned_data[field] is not None:
                        door_data[field] = door_form.cleaned_data[field]
                
                # For rail dimensions, only include if they differ from global defaults
                if global_rail_defaults:
                    if door_form.cleaned_data['rail_top'] is not None and door_form.cleaned_data['rail_top'] != global_rail_defaults.top:
                        door_data['rail_top'] = str(door_form.cleaned_data['rail_top'])
                    if door_form.cleaned_data['rail_bottom'] is not None and door_form.cleaned_data['rail_bottom'] != global_rail_defaults.bottom:
                        door_data['rail_bottom'] = str(door_form.cleaned_data['rail_bottom'])
                    if door_form.cleaned_data['rail_left'] is not None and door_form.cleaned_data['rail_left'] != global_rail_defaults.left:
                        door_data['rail_left'] = str(door_form.cleaned_data['rail_left'])
                    if door_form.cleaned_data['rail_right'] is not None and door_form.cleaned_data['rail_right'] != global_rail_defaults.right:
                        door_data['rail_right'] = str(door_form.cleaned_data['rail_right'])
                
                # Handle removal of existing overrides if values now match global defaults
                existing_keys = set(door_defaults.keys())
                for field in ['rail_top', 'rail_bottom', 'rail_left', 'rail_right']:
                    # If field was in door_defaults but not in door_data, it means
                    # the user changed it to match the global default - we need to explicitly remove it
                    if field in existing_keys and field not in door_data:
                        # Set to None to signal removal
                        door_data[field] = None
                
                # Save door defaults
                customer.set_door_defaults(**door_data)
                messages.success(request, "Door defaults updated successfully")
                return redirect('customer_defaults', customer_id=customer.id)
        else:
            door_form = CustomerDoorDefaultsForm(initial=door_defaults)
            drawer_form = CustomerDrawerDefaultsForm(request.POST)
            
            if drawer_form.is_valid():
                # Extract non-empty values
                drawer_data = {k: v for k, v in drawer_form.cleaned_data.items() if v is not None}
                
                # Save drawer defaults
                customer.set_drawer_defaults(**drawer_data)
                messages.success(request, "Drawer defaults updated successfully")
                return redirect('customer_defaults', customer_id=customer.id)
    else:
        # For GET request, initialize the forms
        door_initial = {}
        drawer_initial = {}
        
        # Process door defaults - convert stored IDs to objects
        for key, value in door_defaults.items():
            # Try to convert string IDs to model objects
            if key == 'wood_stock' and value:
                from ..models.door import WoodStock
                try:
                    door_initial[key] = WoodStock.objects.get(pk=value)
                except (WoodStock.DoesNotExist, ValueError, TypeError):
                    pass
            elif key == 'edge_profile' and value:
                from ..models.door import EdgeProfile
                try:
                    door_initial[key] = EdgeProfile.objects.get(pk=value)
                except (EdgeProfile.DoesNotExist, ValueError, TypeError):
                    pass
            elif key == 'panel_rise' and value:
                from ..models.door import PanelRise
                try:
                    door_initial[key] = PanelRise.objects.get(pk=value)
                except (PanelRise.DoesNotExist, ValueError, TypeError):
                    pass
            elif key == 'style' and value:
                from ..models.door import Style
                try:
                    door_initial[key] = Style.objects.get(pk=value)
                except (Style.DoesNotExist, ValueError, TypeError):
                    pass
            # Try to convert rail dimensions to Decimal
            elif key.startswith('rail_') and value:
                try:
                    door_initial[key] = Decimal(value)
                except (InvalidOperation, TypeError):
                    pass

        # Process drawer defaults
        for key, value in drawer_defaults.items():
            # Try to convert string IDs to model objects
            if key == 'wood_stock' and value:
                from ..models.drawer import DrawerWoodStock
                try:
                    drawer_initial[key] = DrawerWoodStock.objects.get(pk=value)
                except (DrawerWoodStock.DoesNotExist, ValueError, TypeError):
                    pass
            elif key == 'edge_type' and value:
                from ..models.drawer import DrawerEdgeType
                try:
                    drawer_initial[key] = DrawerEdgeType.objects.get(pk=value)
                except (DrawerEdgeType.DoesNotExist, ValueError, TypeError):
                    pass
            elif key == 'bottom' and value:
                from ..models.drawer import DrawerBottomSize
                try:
                    drawer_initial[key] = DrawerBottomSize.objects.get(pk=value)
                except (DrawerBottomSize.DoesNotExist, ValueError, TypeError):
                    pass
            # Boolean fields can be used directly
            elif key in ['undermount', 'finishing']:
                drawer_initial[key] = value
        
        door_form = CustomerDoorDefaultsForm(initial=door_initial)
        drawer_form = CustomerDrawerDefaultsForm(initial=drawer_initial)
    
    context = {
        'customer': customer,
        'door_form': door_form,
        'drawer_form': drawer_form,
        'title': f'Defaults for {customer.company_name.title()}',
        'global_rail_defaults': global_rail_defaults
    }
    
    return render(request, 'customer/customer_defaults.html', context) 