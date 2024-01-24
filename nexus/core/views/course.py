import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from . import restrict_to_http_methods

from ..forms.course import (
    CourseForm,
)

from ..models import (
    Course,
    CourseSubject,
)

@login_required
@restrict_to_http_methods('GET', 'POST')
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(False, request.POST)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'create_course_response.html', context={'success': False})
        data = form.cleaned_data
        if data['is_cross_listed']:
            if data['main_course'] is None:
                messages.error(request, 'Cross listed course must have a main course.')
                return render(request, 'create_course_response.html', context={'success': False})
            if data['main_course'].is_cross_listed:
                messages.error(request, 'The main course you have added is itself a crosslisted course. Main course can not be a crosslisted course.')
                return render(request, 'create_course_response.html', context={'success': False})
        elif data['main_course'] is not None:
            messages.error(request, 'Main course can only be added for crosslisted courses.')
            return render(request, 'create_course_response.html', context={'success': False})
        course = form.save()
        messages.success(request, 'Course created successfully.')
        form = CourseForm(False)
        context = {'form': form, 'success': True, 'course': course}
        response = render(request, 'create_course_response.html', context=context)
        response["HX-Trigger-After-Settle"] = json.dumps({"courseCreated": f"ct-{course.id}"})
        return response
    form = CourseForm(False)
    context = {
        'form': form,
    }
    return render(request, 'just_form.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
def edit_course(request, course_id):
    if request.method == 'POST':
        form = CourseForm(True, request.POST, instance=Course.objects.get(id=course_id))
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'edit_course_response.html', context={'success': False})
        data = form.cleaned_data
        if data['is_cross_listed']:
            if data['main_course'] is None:
                messages.error(request, 'Cross listed course must have a main course.')
                return render(request, 'edit_course_response.html', context={'success': False})
            if data['main_course'].is_cross_listed:
                messages.error(request, 'The main course you have added is itself a crosslisted course. Main course can not be a crosslisted course.')
                return render(request, 'edit_course_response.html', context={'success': False})
        elif data['main_course'] is not None:
            messages.error(request, 'Main course can only be added for crosslisted courses.')
            return render(request, 'edit_course_response.html', context={'success': False})
        Course.objects.filter(id=course_id).update(**data)
        messages.success(request, 'Course updated successfully.')
        context = {'success': True, 'course': Course.objects.get(id=course_id)}
        return render(request, 'edit_course_response.html', context=context)
    form = CourseForm(True, instance=Course.objects.get(id=course_id))
    context = {
        'form': form,
    }
    response = render(request, 'just_form.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"courseUpdateClicked": f"ct-{course_id}"})
    return response

@login_required
@restrict_to_http_methods('GET')
def list_courses(request):
    courses = Course.objects.all()
    context = { 'courses': courses }
    return render(request, 'courses.html', context)