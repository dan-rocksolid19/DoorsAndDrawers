from django.urls import path
from ..views.quote import quotes, quote_detail, create_quote, delete_quote, convert_to_order
from ..views.order import quote_search

urlpatterns = [
    path('', quotes, name='quotes'),
    path('create/', create_quote, name='new_quote'),
    path('<int:id>/', quote_detail, name='quote_detail'),
    path('<int:id>/delete/', delete_quote, name='delete_quote'),
    path('<int:id>/convert/', convert_to_order, name='convert_to_order'),
    path('search/', quote_search, name='quote_search'),
] 