from django.urls import path
from ..views.order import orders, order_detail, create_order, delete_order, get_customer_details

urlpatterns = [
    path('', orders, name='orders'),
    path('create/', create_order, name='new_order'),
    path('<int:id>/', order_detail, name='order_detail'),
    path('<int:id>/delete/', delete_order, name='delete_order'),
    path('get-customer-address/', get_customer_details, name='get_customer_address'),
] 