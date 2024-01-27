from django.shortcuts import render, redirect

from . import restrict_to_http_methods, restrict_to_groups
from django.contrib.auth.decorators import login_required

from ..forms.building import (
    BuildingsForm,
)

from ..models import (
    Buildings,
)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin')
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

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin')
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

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin')
def list_buildings(request):
    buildings = Buildings.objects.all()
    context = { 'buildings': buildings }
    return render(request, 'buildings.html', context)