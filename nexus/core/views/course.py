from django.shortcuts import render, redirect
from django.contrib import messages

from . import restrict_to_http_methods

from ..forms.course import (
    CourseForm,
)

from ..models import (
    Course,
    CourseSubject,
)

@restrict_to_http_methods('GET', 'POST')
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_courses')
    messages.add_message(request, messages.ERROR, f"Form errors: An example danger alert with an icon", extra_tags='alert-dismissible')
    form = CourseForm()
    context = {
        'title': 'Add Course',
        'form': form,
        'post_url': 'create_course',
    }
    return render(request, 'genric_form.html', context)

@restrict_to_http_methods('GET', 'POST')
def edit_course(request, course_id):
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=Course.objects.get(id=course_id))
        if form.is_valid():
            form.save()
            return redirect('list_courses')
    form = CourseForm(instance=Course.objects.get(id=course_id))
    context = {
        'title': 'Edit Course',
        'form': form,
        'post_url': 'edit_course',
        'post_arg': course_id,
    }
    return render(request, 'genric_form.html', context)

@restrict_to_http_methods('GET')
def list_courses(request):
    courses = Course.objects.all()
    context = { 'courses': courses }
    return render(request, 'courses.html', context)