from django.urls import path, include
from ..views import home

urlpatterns = [
    path('', home, name='home'),
    path('customers/', include('core.urls.customer')),
    path('orders/', include('core.urls.order')),
    path('quotes/', include('core.urls.quote')),
    path('doors/', include('core.urls.door')),
] 