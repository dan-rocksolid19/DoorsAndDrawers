from django.urls import path
from ..views import customers, customer_detail, new_customer, edit_customer, delete_customer

urlpatterns = [
    path('', customers, name='customers'),
    path('create/', new_customer, name='new_customer'),
    path('<int:id>/', customer_detail, name='customer_detail'),
    path('<int:id>/edit/', edit_customer, name='edit_customer'),
    path('<int:id>/delete/', delete_customer, name='delete_customer'),
] 