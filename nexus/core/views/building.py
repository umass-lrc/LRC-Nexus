from django.shortcuts import render, redirect

from . import restrict_to_http_methods

from ..forms.building import (
    BuildingsForm,
)

from ..models import (
    Buildings,
)

@restrict_to_http_methods('GET', 'POST')
def create_building(request):
    if request.method == 'POST':
        form = BuildingsForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('create_building')
    context = {
        'title': 'Add Building',
        'form': BuildingsForm(),
        'post_url': 'create_building',
    }
    return render(request, 'genric_form.html', context)

@restrict_to_http_methods('GET', 'POST')
def edit_building(request, building_short_name):
    if request.method == 'POST':
        form = BuildingsForm(request.POST, instance=Buildings.objects.get(short_name=building_short_name))
        if form.is_valid():
            form.save()
        return redirect('edit_building', building_short_name)
    context = {
        'title': 'View/Edit Building',
        'form': BuildingsForm(instance=Buildings.objects.get(short_name=building_short_name), button='Save Changes'),
        'post_url': 'edit_building',
        'post_arg': building_short_name,
    }
    return render(request, 'genric_form.html', context)

@restrict_to_http_methods('GET')
def list_buildings(request):
    buildings = Buildings.objects.all()
    context = { 'buildings': buildings }
    return render(request, 'buildings.html', context)