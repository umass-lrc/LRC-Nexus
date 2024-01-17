from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect


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
        if form.is_valid():
            form.save()
            return redirect('semester_details', semester_id=form.instance.id)
    form = SemesterForm()
    context = {
        'title': 'Create Semester',
        'form': form,
        'post_url': 'create_semester',
    }
    return render(request, 'genric_form.html', context)

@restrict_to_http_methods('GET')
def semester_details(request, semester_id):
    context = {
        'semester_form': SemesterReadOnly(instance=Semester.objects.get(id=semester_id)),
        'sem_id': semester_id,
    }
    return render(request, 'semester_details.html', context)

@restrict_to_http_methods('GET')
def list_holidays(request, semester_id):
    semester = Semester.objects.get(id=semester_id)
    holidays = Holiday.objects.filter(semester=semester)
    form = HolidayForm()
    context = {
        'holidays': holidays,
        'form': form,
        'post_url': 'add_holiday',
        'sem_id': semester_id,
    }
    return render(request, 'holidays.html', context)

@restrict_to_http_methods('POST')
def add_holiday(request, semester_id):
    form = HolidayForm(request.POST)
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
    form = DaySwitchForm()
    context = {
        'day_switches': day_switches,
        'form': form,
        'post_url': 'add_day_switch',
        'sem_id': semester_id,
    }
    return render(request, 'day_switches.html', context)

@restrict_to_http_methods('POST')
def add_day_switch(request, semester_id):
    form = DaySwitchForm(request.POST)
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