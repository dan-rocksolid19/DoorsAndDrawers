from django.urls import path
from ..views.order import (
    orders, order_detail, create_order, delete_order,
    get_customer_details, order_search, remove_line_item
)
from ..views.common import generate_order_pdf

urlpatterns = [
    path('', orders, name='orders'),
    path('create/', create_order, name='new_order'),
    path('<int:order_id>/', order_detail, name='order_detail'),
    path('<int:order_id>/delete/', delete_order, name='delete_order'),
    path('<int:order_id>/pdf/', generate_order_pdf, name='order_pdf'),
    path('get-customer-address/', get_customer_details, name='get_customer_address'),
    path('search/', order_search, name='order_search'),
    path('items/<int:item_id>/remove/', remove_line_item, name='remove_line_item'),
] 