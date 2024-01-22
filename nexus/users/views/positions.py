from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from core.views import restrict_to_http_methods

from ..models import (
    Positions,
)

from ..forms.positions import (
    PositionSelector,
    PositionForm,
)

@login_required
@restrict_to_http_methods('GET')
def get_all_positions(request, semester_id, position):
    positions = Positions.objects.filter(semester_id=semester_id, position=position).all()
    context = {'positions': positions}
    return render(request, 'requested_positions.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
def positions(request):
    if request.method == 'POST':
        form = PositionSelector(request.POST)
        if not form.is_valid():
            return 
        data = form.cleaned_data
        semester = data['semester']
        position = data['position']
        context = {'semester': semester.id, 'position': position}
        return render(request, 'position_post.html', context)
    form = PositionSelector()
    context = {'form': form}
    return render(request, 'positions.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
def add_position(request, semester_id=None, position_id=None):
    if request.method == 'POST':
        POST = request.POST.copy()
        POST['semester'] = semester_id
        POST['position'] = position_id
        form = PositionForm(POST, initial={'semester': semester_id, 'position': position_id})
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'alerts.html')
        data = form.cleaned_data
        form.save()
        messages.success(request, 'Position added successfully.')
        return redirect('get_all_positions', semester_id=data['semester'].id, position=data['position'])
    form = None
    if semester_id is None and position_id is None:
        form = PositionForm()
    else:
        form = PositionForm(initial={'semester': semester_id, 'position': position_id})
    context = {'form': form}
    return render(request, 'just_form.html', context)

@login_required
@restrict_to_http_methods('GET')
def delete_position(request, position_id):
    pass