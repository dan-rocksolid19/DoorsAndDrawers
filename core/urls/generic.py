from django.urls import path
from ..views.line_item import generic_item_form, add_generic_item

urlpatterns = [
    path('form/', generic_item_form, name='generic_item_form'),
    path('add/', add_generic_item, name='add_generic_item'),
] 