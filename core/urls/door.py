from django.urls import path
from ..views import door_form, add_door

urlpatterns = [
    path('form/', door_form, name='door_form'),
    path('add/', add_door, name='new_door'),
] 