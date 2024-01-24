from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from ..models import (
    Semester,
    Holiday,
    DaySwitch,
)

from ..forms.semester import (
    SemesterForm,
    SemesterReadOnly,
    HolidayForm,
    DaySwitchForm,
)

from . import restrict_to_http_methods

import json

@restrict_to_http_methods('GET', 'POST')
def create_semester(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'create_semester_response.html', context={'success': False})
        semester = form.save()
        form = SemesterForm()
        messages.success(request, 'Semester created successfully.')
        context = {'form': form, 'success': True, 'semester': semester}
        response = render(request, 'create_semester_response.html', context=context)
        response["HX-Trigger-After-Settle"] = json.dumps({"semesterCreated": f"st-{semester.id}"})
        return response
    form = SemesterForm()
    context = {'form': form}
    return render(request, 'just_form.html', context)

@restrict_to_http_methods('GET')
def semester_details(request, semester_id):
    context = {
        'semester_form': SemesterReadOnly(instance=Semester.objects.get(id=semester_id)),
        'sem_id': semester_id,
    }
    response = render(request, 'semester_details.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"semesterUpdateClicked": f"st-{semester_id}"})
    return response

@restrict_to_http_methods('GET')
def list_holidays(request, semester_id):
    semester = Semester.objects.get(id=semester_id)
    holidays = Holiday.objects.filter(semester=semester)
    form = HolidayForm(semester_id)
    context = {
        'holidays': holidays,
        'form': form,
    }
    return render(request, 'holidays.html', context)

@restrict_to_http_methods('POST')
def add_holiday(request, semester_id):
    form = HolidayForm(semester_id, request.POST)
    semester = Semester.objects.get(id=semester_id)
    if form.is_valid():
        data = form.cleaned_data
        Holiday.objects.create(
            semester=semester,
            date=data['date'],
        )
    return redirect('list_holidays', semester_id=semester_id)

@restrict_to_http_methods('GET')
def list_day_switches(request, semester_id):
    semester = Semester.objects.get(id=semester_id)
    day_switches = DaySwitch.objects.filter(semester=semester)
    form = DaySwitchForm(semester_id)
    context = {
        'day_switches': day_switches,
        'form': form,
    }
    return render(request, 'day_switches.html', context)

@restrict_to_http_methods('POST')
def add_day_switch(request, semester_id):
    form = DaySwitchForm(semester_id, request.POST)
    semester = Semester.objects.get(id=semester_id)
    if form.is_valid():
        data = form.cleaned_data
        DaySwitch.objects.create(
            semester=semester,
            date=data['date'],
            day_to_follow=data['day_to_follow'],
        )
    return redirect('list_day_switches', semester_id=semester_id)

@restrict_to_http_methods('GET')
def list_semesters(request):
    semesters = Semester.objects.all()
    context = {
        'semesters': semesters,
    }
    return render(request, 'semesters.html', context)

@csrf_protect
@restrict_to_http_methods('PUT')
def change_active_semester(request, semester_id):
    semester = Semester.objects.get(id=semester_id)
    body_unicode = request.body.decode('utf-8')
    active = len(body_unicode.split('=')) == 2
    context = {
        'active': active,
        'old_id': -1,
    }
    
    if active:
        if Semester.objects.get_active_semester() is not None:
            active_sem = Semester.objects.get_active_semester()
            context['old_id'] = active_sem.id
            active_sem.active = False
            active_sem.save()
        semester.active = True
        semester.save()
    else:
        semester.active = False
        semester.save()
            
    return render(request, "switch.html", context)