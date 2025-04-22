"""
Common view functions for order and quote listings and search functionality.
"""
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from django_htmx.http import retarget, reswap


def paginate_queryset(queryset, page, per_page=10):
    """
    Paginate a queryset.
    
    Args:
        queryset: The queryset to paginate
        page: The current page number
        per_page: Number of items per page
        
    Returns:
        paginated queryset
    """
    paginator = Paginator(queryset, per_page)
    
    try:
        paginated_items = paginator.page(page)
    except PageNotAnInteger:
        paginated_items = paginator.page(1)
    except EmptyPage:
        paginated_items = paginator.page(paginator.num_pages)
        
    return paginated_items, paginator


def search_and_filter_orders(queryset, search_params):
    """
    Apply common search and filter criteria to an order or quote queryset.
    
    Args:
        queryset: The base queryset of Order objects
        search_params: Dictionary containing search parameters
            - min_id: Minimum order ID
            - max_id: Maximum order ID
            - start_date: Start date for filtering
            - end_date: End date for filtering
            - customer_search: Customer name search term
            
    Returns:
        Filtered queryset
    """
    # Extract search parameters
    min_id = search_params.get('min_id', '')
    max_id = search_params.get('max_id', '')
    start_date = search_params.get('start_date', '')
    end_date = search_params.get('end_date', '')
    customer_query = search_params.get('customer_search', '').strip()
    
    # Apply ID filters if provided
    if min_id and min_id.isdigit():
        queryset = queryset.filter(id__gte=int(min_id))
    
    if max_id and max_id.isdigit():
        queryset = queryset.filter(id__lte=int(max_id))
    
    # Apply date filters if provided
    try:
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
    except ValueError:
        # If date format is invalid, continue without date filtering
        pass
    
    # Apply customer filter if provided
    if customer_query:
        queryset = queryset.filter(customer__company_name__icontains=customer_query)
    
    # Order by descending order date (newest first)
    queryset = queryset.order_by('-order_date')
    
    return queryset


def handle_entity_search(request, base_queryset, template_name, entity_name='items'):
    """
    Handle search, filtering and pagination for orders/quotes in a single function.
    
    Args:
        request: The HTTP request object
        base_queryset: The base queryset to search and filter (e.g., Order.confirmed.all())
        template_name: The template to render results in
        entity_name: The name to use for the entities in the template context
        
    Returns:
        Rendered response with filtered, paginated results
    """
    # Extract search parameters
    search_params = {
        'min_id': request.GET.get('min_id', ''),
        'max_id': request.GET.get('max_id', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'customer_search': request.GET.get('customer_search', '').strip()
    }
    page = request.GET.get('page', 1)

    # Apply filters
    filtered_query = search_and_filter_orders(base_queryset, search_params)
    
    # Paginate the results
    paginated_items, paginator = paginate_queryset(filtered_query, page)

    # Prepare context
    context = {
        entity_name: paginated_items,
        'min_id': search_params['min_id'],
        'max_id': search_params['max_id'],
        'start_date': search_params['start_date'],
        'end_date': search_params['end_date'],
        'customer_search': search_params['customer_search'],
        'paginator': paginator
    }
    
    # Render the template
    return render(request, template_name, context)


def handle_entity_list(request, base_queryset, template_name, entity_name='items', title=None):
    """
    Handle listing entities (orders/quotes) with pagination.
    
    Args:
        request: The HTTP request object
        base_queryset: The base queryset to paginate
        template_name: The template to render
        entity_name: The name to use for the entities in context
        title: The title for the page
        
    Returns:
        Rendered response with paginated results
    """
    # Get page number
    page = request.GET.get('page', 1)
    
    # Use common pagination function
    paginated_items, paginator = paginate_queryset(base_queryset, page)
    
    # Prepare context
    context = {
        entity_name: paginated_items,
        'paginator': paginator,
        'min_id': '',
        'max_id': '',
        'start_date': '',
        'end_date': '',
        'customer_search': '',
    }
    
    # Add title if provided
    if title:
        context['title'] = title
    
    # Render the template
    return render(request, template_name, context)


def render_form_with_errors(request, form, item_type, error_message=None):
    """
    Helper function to render a form with errors and retarget it to the form container.
    
    Args:
        request: The HTTP request
        form: The form with errors
        item_type: The type of item ('door', 'drawer', etc.)
        error_message: Optional error message to add to the form
        
    Returns:
        Rendered response with HTMX retargeting and appropriate status code
    """
    if error_message:
        form.add_error(None, error_message)
        
    template_name = f"{item_type}/{item_type}_form.html"
    response = render(request, template_name, {'form': form}, status=422)  # Return 422 Unprocessable Entity for validation errors
    return retarget(reswap(response, "outerHTML"), "#door-form-container")


def process_line_item_form(request, form_class, model_class, item_type, transform_data_func=None):
    """
    Process a line item form (door, drawer, etc.) and add to session.
    
    Args:
        request: The HTTP request
        form_class: The form class to use for validation
        model_class: The model class to use for price calculation
        item_type: Type of item ('door', 'drawer', etc.)
        transform_data_func: Optional function to transform cleaned data to session data
        
    Returns:
        Rendered response or JsonResponse (error)
    """
    try:
        # Initialize order in session if it doesn't exist
        if 'current_order' not in request.session:
            request.session['current_order'] = {
                'items': []
            }
            request.session.modified = True
        
        # Initialize items array if it doesn't exist
        if 'items' not in request.session['current_order']:
            request.session['current_order']['items'] = []
            request.session.modified = True
        
        # Use the form for validation
        form = form_class(request.POST)
        
        if not form.is_valid():
            # Render form with validation errors
            return render_form_with_errors(request, form, item_type)
            
        # Get cleaned data
        cleaned_data = form.cleaned_data
        
        # Extract custom price information
        custom_price = request.POST.get('custom_price') == 'on'
        price_per_unit_manual = request.POST.get('price_per_unit_manual')
        
        # Create a model instance for price calculation
        try:
            item_model = model_class(**cleaned_data)
        except Exception as e:
            # Return form with error message for model creation issues
            return render_form_with_errors(request, form, item_type, f'Could not create {item_type}: {str(e)}')
        
        # Apply custom price if provided
        if custom_price and price_per_unit_manual:
            try:
                price_value = Decimal(price_per_unit_manual)
                if price_value <= 0:
                    raise ValueError("Price must be greater than zero")
                    
                item_model.custom_price = True
                item_model.price_per_unit = price_value
            except (InvalidOperation, ValueError) as e:
                # If price_per_unit_manual is not valid, use calculated price
                item_model.custom_price = False
                item_model.price_per_unit = item_model.calculate_price()
        else:
            item_model.custom_price = False
            item_model.price_per_unit = item_model.calculate_price()
        
        # Get the calculated price
        try:
            price = item_model.price
        except Exception as e:
            # Return form with error message for price calculation issues
            return render_form_with_errors(request, form, item_type, f'Error calculating price: {str(e)}')
        
        # Create session item data
        try:
            if transform_data_func:
                # Use custom transformation function if provided
                session_item = transform_data_func(cleaned_data, item_model, item_type, custom_price, price)
            else:
                # Default transformation (will need customization per item type)
                session_item = {
                    'type': item_type,
                    'quantity': str(cleaned_data['quantity']),
                    'price_per_unit': str(item_model.price_per_unit),
                    'total_price': str(price),
                    'custom_price': custom_price
                }
        except Exception as e:
            # Return form with error message for data preparation issues
            return render_form_with_errors(request, form, item_type, f'Error preparing item data: {str(e)}')
        
        # Add the item to the session order
        try:
            request.session['current_order']['items'].append(session_item)
            # Mark session as modified
            request.session.modified = True
        except Exception as e:
            # Return form with error message for session update issues
            return render_form_with_errors(request, form, item_type, f'Error saving item to order: {str(e)}')
        
        # Return updated line items table (success case - unmodified)
        response = render(request, 'door/line_items_table.html', {
            'items': request.session['current_order']['items']
        })
        # No need to add retarget for success case as we'll use the default target
        return response
        
    except Exception as e:
        # Handle unexpected errors
        form = form_class(request.POST)
        return render_form_with_errors(request, form, item_type, str(e))