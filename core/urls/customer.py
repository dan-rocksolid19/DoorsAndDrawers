from django.urls import path
from ..views.customer import customers, customer_detail, new_customer, edit_customer, delete_customer, customer_search, customer_defaults

urlpatterns = [
    path('', customers, name='customers'),
    path('create/', new_customer, name='new_customer'),
    path('<int:customer_id>/', customer_detail, name='customer_detail'),
    path('<int:customer_id>/edit/', edit_customer, name='edit_customer'),
    path('<int:customer_id>/delete/', delete_customer, name='delete_customer'),
    path('search/', customer_search, name='customer_search'),
    path('<int:customer_id>/defaults/', customer_defaults, name='customer_defaults'),
] 