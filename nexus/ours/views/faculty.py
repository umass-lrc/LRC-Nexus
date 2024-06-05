from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.db.models import CharField, Value
from django.db.models.functions import Concat

import json
from dal import autocomplete

from core.views import restrict_to_http_methods, restrict_to_groups

from ..models import (
    Faculty,
    FacultyDetails,
    FacultyPosition,
    Keyword,
)

from ..forms.faculty import UpdateFacultyDetailsForm, SimpleSearchForm

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def faculty_list(request):
    if request.method == 'POST':
        search = request.POST.get('search').strip()
        if len(search) == 0:
            faculties = FacultyDetails.objects.all()
        else:
            faculties = FacultyDetails.objects.basic_search(search)
        context = {
            'faculties': faculties.values_list('faculty_id', flat=True),
        }
        return render(request, 'faculty_simple_search_result.html', context)
    faculties = FacultyDetails.objects.all()
    not_added = Faculty.objects.exclude(id__in=faculties.values_list('faculty__id', flat=True))
    for faculty in not_added:
        FacultyDetails.objects.create(faculty=faculty)
    faculties = FacultyDetails.objects.all()
    context = {
        'faculties': faculties.values_list('faculty_id', flat=True),
        'form': SimpleSearchForm(),
    }
    return render(request, 'faculty_list.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def get_faculty_row(request, faculty_id):
    faculty = FacultyDetails.objects.get(faculty_id=faculty_id)
    context = {'faculty': faculty, 'faculty_id': faculty_id}
    return render(request, 'faculty_row.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def update_faculty_details(request, faculty_id):
    faculty = FacultyDetails.objects.get(faculty_id=faculty_id)
    if request.method == 'POST':
        updated_post = request.POST.copy()
        positions = request.POST.getlist('positions')
        keywords = request.POST.getlist('keywords')
        for i, position in enumerate(positions):
            if position.isnumeric() and FacultyPosition.objects.filter(id=int(position)).exists():
                continue
            pos = FacultyPosition.objects.get_or_create(position=position)
            positions[i] = str(pos.id)
        updated_post.setlist('positions', positions)
        for i, keyword in enumerate(keywords):
            if keyword.isnumeric() and Keyword.objects.filter(id=int(keyword)).exists():
                continue
            key = Keyword.objects.get_or_create(keyword=keyword)[0]
            keywords[i] = str(key.id)
        updated_post.setlist('keywords', keywords)
        form = UpdateFacultyDetailsForm(updated_post, instance=faculty)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
        else:
            form.save()
            messages.success(request, 'Faculty details updated successfully.')
        context = {'success': True, 'faculty': faculty, 'faculty_id': faculty_id}
        response = render(request, 'update_faculty.html', context)
        response["HX-Trigger-After-Settle"] = json.dumps({"facultyDetailsUpdated": ""})
        return response
    context = {'success':False, 'faculty': faculty, 'faculty_id': faculty_id}
    response = render(request, 'update_faculty.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"updateClicked": f"ft-{faculty.faculty_id}"})
    return response

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def update_faculty_details_form(request, faculty_id):
    faculty = FacultyDetails.objects.get(faculty_id=faculty_id)
    form = UpdateFacultyDetailsForm(instance=faculty)
    context = {'form': form}
    return render(request, 'just_form.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'OURS Supervisor', 'Staff-OURS-Mentor')
def view_faculty_details(request, faculty_id):
    faculty = FacultyDetails.objects.get(faculty_id=faculty_id)
    positions = ', '.join(map( str, faculty.positions.all()))
    positions = 'None' if len(positions) == 0 else positions
    subjects = ', '.join(map( str, faculty.subjects.all()))
    subjects = 'None' if len(subjects) == 0 else subjects
    keywords = ','.join(map( str, faculty.keywords.all()))
    keywords = 'None' if len(keywords) == 0 else keywords
    context = {'faculty': faculty, 'positions': positions, 'subjects': subjects, 'keywords': keywords}
    response = render(request, 'faculty_details.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"viewClicked": f"ft-{faculty.faculty_id}"})
    return response

class FacultyAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = FacultyDetails.objects.all()
        if self.q:
            qs = FacultyDetails.objects.basic_search(self.q)
        return qs