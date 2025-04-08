from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from ..forms import DoorForm

@require_http_methods(["GET", "POST"])
def door_form(request):
    """
    View to handle the door form.
    GET: Returns the form template
    POST: Processes the form data
    """
    form = DoorForm()
    
    # If this is a POST request, process the form data
    if request.method == 'POST':
        form = DoorForm(request.POST)
        if form.is_valid():
            # In a real scenario, we might create and save the door
            # door = form.save()
            pass
    
    # Return the form template
    return render(request, 'door/door_form.html', {
        'form': form,
    })

@require_http_methods(["POST"])
def add_door(request):
    """
    View to handle adding a door.
    """
    # Empty response for now
    return HttpResponse("")