from django.shortcuts import render, redirect

from . import restrict_to_http_methods

from ..forms.faculty import (
    FacultyForm,
)

from ..models import (
    Faculty,
)

@restrict_to_http_methods('GET', 'POST')
def create_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('create_faculty')
    context = {
        'title': 'Create Faculty',
        'form': FacultyForm(),
        'post_url': 'create_faculty',
    }
    return render(request, 'genric_form.html', context)

@restrict_to_http_methods('GET', 'POST')
def edit_faculty(request, faculty_id):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            faculty = Faculty.objects.get(id=faculty_id)
            data = form.cleaned_data
            faculty.first_name = data['first_name']
            faculty.last_name = data['last_name']
            faculty.email = data['email']
            faculty.save()
        return redirect('edit_faculty', faculty_id)
    context = {
        'title': 'View/Edit Faculty',
        'form': FacultyForm(instance=Faculty.objects.get(id=faculty_id), button='Save Changes'),
        'post_url': 'edit_faculty',
        'post_arg': faculty_id,
    }
    return render(request, 'genric_form.html', context)

@restrict_to_http_methods('GET')
def list_faculties(request):
    faculties = Faculty.objects.all()
    context = { 'faculties': faculties }
    return render(request, 'faculties.html', context)