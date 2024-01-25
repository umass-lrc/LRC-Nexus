import json
from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render
from . import restrict_to_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..forms.classes import (
    semesterSelector,
    createClassForm,
    addClassTimeForm,
)

from ..models import (
    Classes,
    Semester,
    ClassTimes,
)

@login_required
@restrict_to_http_methods('GET', 'POST')
def all_classes(request):
    if request.method == 'POST':
        form = semesterSelector(request.POST)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'classes_semester_response.html', context={'success': False})
        data = form.cleaned_data
        semester = data['semester']
        classes = Classes.objects.filter(semester=semester).all()
        context = {'success': True, 'classes': classes, 'semester_id': semester.id}
        return render(request, 'classes_semester_response.html', context)
    form = semesterSelector()
    context = {'form': form}
    return render(request, 'classes.html', context)

@restrict_to_http_methods('GET', 'POST')
def create_class(request, semester_id):
    if request.method == 'POST':
        sem = Semester.objects.get(id=semester_id)
        POST = request.POST.copy()
        POST['semester'] = sem
        form = createClassForm(POST, initial={'semester': sem})
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'create_class_response.html', context={'success': False})
        _class = form.save()
        messages.success(request, 'Class created successfully.')
        context = {'success': True, 'class': _class, 'semester_id': semester_id}
        response = render(request, 'create_class_response.html', context)
        response["HX-Trigger-After-Settle"] = json.dumps({"classCreated": f"ct-{_class.id}"})
        return response
    semester = Semester.objects.get(id=semester_id)
    form = createClassForm(initial={'semester': semester})
    context = {'form': form}
    return render(request, 'just_form.html', context)

@restrict_to_http_methods('GET', 'POST')
def edit_class(request, class_id):
    _class = Classes.objects.get(id=class_id)
    if request.method == "POST":
        POST = request.POST.copy()
        POST['semester'] = _class.semester
        form = createClassForm(request.POST, edit=True, instance=_class)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'edit_class_response.html', context={'success': False})
        Classes.objects.filter(id=class_id).update(**form.cleaned_data)
        messages.success(request, 'Class updated successfully.')
        context = {'success': True, 'class': _class}
        return render(request, 'edit_class_response.html', context)
    form = createClassForm(edit=True, instance=_class)
    class_times = ClassTimes.objects.filter(orignal_class=_class).all()
    context = {'form': form, 'class_times': class_times, 'class_id': class_id}
    response = render(request, 'edit_class.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"classUpdateClicked": f"ct-{class_id}"})
    return response

@restrict_to_http_methods('GET','POST')
def add_class_time(request, class_id):
    if request.method == "POST":
        form = addClassTimeForm(class_id, request.POST)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'add_class_time_response.html', context={'success': False})
        data = form.cleaned_data
        class_time = ClassTimes.objects.create(
            orignal_class=Classes.objects.get(id=class_id),
            class_day=data['class_day'],
            start_time=data['start_time'],
            duration=timedelta(hours=data['hours'], minutes=data['minutes']),
            building=data['building'],
            room=data['room'],
        )
        _class = Classes.objects.get(id=class_id)
        messages.success(request, 'Class time added successfully.')
        context = {'success': True, 'class_time': class_time, 'class': _class}
        return render(request, 'add_class_time_response.html', context)
    form = addClassTimeForm(class_id)
    context = {'form': form}
    return render(request, 'just_form.html', context)

@restrict_to_http_methods('DELETE')
def delete_class_time(request, class_time_id):
    class_time = ClassTimes.objects.get(id=class_time_id)
    _class = class_time.orignal_class 
    class_time.delete()
    context = {'class': _class}
    response = render(request, 'delete_class_time_response.html', context)
    response["HX-Trigger"] = json.dumps({"deleteClassTime": f"ctt-{class_time_id}"})
    return response
