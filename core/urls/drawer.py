from django.urls import path
from ..views import drawer_form, add_drawer

urlpatterns = [
    path('form/', drawer_form, name='drawer_form'),
    path('add/', add_drawer, name='new_drawer'),
] 