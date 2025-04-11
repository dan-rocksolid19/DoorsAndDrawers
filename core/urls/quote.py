from django.urls import path
from ..views.quote import quotes, quote_detail, create_quote, delete_quote, convert_to_order, generate_quote_pdf, quote_search

urlpatterns = [
    path('', quotes, name='quotes'),
    path('create/', create_quote, name='new_quote'),
    path('<int:quote_id>/', quote_detail, name='quote_detail'),
    path('<int:quote_id>/delete/', delete_quote, name='delete_quote'),
    path('<int:quote_id>/convert/', convert_to_order, name='convert_to_order'),
    path('<int:quote_id>/pdf/', generate_quote_pdf, name='quote_pdf'),
    path('search/', quote_search, name='quote_search'),
] 