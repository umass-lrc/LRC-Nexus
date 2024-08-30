import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from . import restrict_to_http_methods, restrict_to_groups

from ..forms.faculty import (
    FacultyForm,
)

from ..models import (
    Faculty,
)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'SI Supervisor')
def create_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(False, request.POST)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'create_faculty_response.html', context={'success': False})
        faculty = form.save()
        messages.success(request, 'Faculty created successfully.')
        form = FacultyForm(False)
        context = {'success': True, 'faculty': faculty, 'form': form}
        response = render(request, 'create_faculty_response.html', context)
        response["HX-Trigger-After-Settle"] = json.dumps({"facultyCreated": f"ft-{faculty.id}"})
        return response
    context = {
        'form': FacultyForm(False),
    }
    return render(request, 'just_form.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'SI Supervisor')
def edit_faculty(request, faculty_id):
    if request.method == 'POST':
        form = FacultyForm(True, request.POST, instance=Faculty.objects.get(id=faculty_id))
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'edit_faculty_response.html', context={'success': False})
        Faculty.objects.filter(id=faculty_id).update(**form.cleaned_data)
        faculty = Faculty.objects.get(id=faculty_id)
        messages.success(request, 'Faculty updated successfully.')
        context = {'success': True, 'faculty': faculty}
        return render(request, 'edit_faculty_response.html', context)
    context = {'form': FacultyForm(True, instance=Faculty.objects.get(id=faculty_id)),}
    response = render(request, 'just_form.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"facultyUpdateClicked": f"ft-{faculty_id}"})
    return response

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'SI Supervisor')
def list_faculties(request):
    faculties = Faculty.objects.all()
    context = { 'faculties': faculties }
    return render(request, 'faculties.html', context)