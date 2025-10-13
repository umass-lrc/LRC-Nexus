import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from . import restrict_to_http_methods, restrict_to_groups

from ..forms.course import (
    CourseForm,
)

from ..models import (
    Course,
    CourseSubject,
    Semester,
)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'Tutor Supervisor', 'SI Supervisor')
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
@restrict_to_groups('Staff Admin', 'Tutor Supervisor', 'SI Supervisor')
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
@restrict_to_groups('Staff Admin', 'Tutor Supervisor', 'SI Supervisor')
def list_courses(request):
    # Optimize: Use select_related to avoid N+1 queries for course subjects
    courses_queryset = Course.objects.select_related('subject', 'main_course', 'main_course__subject').order_by('subject__short_name', 'number')
    
    # Add smart pagination - only paginate if there are many courses
    course_count = courses_queryset.count()
    if course_count > 100:  # Only paginate if more than 100 courses
        paginator = Paginator(courses_queryset, 50)  # Show 50 courses per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        context = { 
            'courses': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'total_courses': course_count
        }
    else:
        # Show all courses if not too many
        context = { 
            'courses': courses_queryset,
            'total_courses': course_count
        }
    
    return render(request, 'courses.html', context)