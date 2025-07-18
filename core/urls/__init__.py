from django.urls import path, include
from django.views.generic.base import RedirectView
from ..views import home

urlpatterns = [
    path('',RedirectView.as_view(url='home/')),
    path('home/', home, name='home'),
    path('customers/', include('core.urls.customer')),
    path('orders/', include('core.urls.order')),
    path('quotes/', include('core.urls.quote')),
    path('doors/', include('core.urls.door')),
    path('drawers/', include('core.urls.drawer')),
    path('generic/', include('core.urls.generic')),
    path('settings/', include('core.urls.settings')),
] 