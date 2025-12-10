import json
from datetime import datetime, timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from django.db.models import Q

from dal import autocomplete

from core.views import restrict_to_http_methods, restrict_to_groups

from core.models import (
    Semester,
    Course,
)

from users.models import (
    NexusUser,
    Positions,
    PositionChoices,
)

from ..models import (
    Shift,
    RecurringShift,
    ShiftKind,
)

from ..forms.users_shift import (
    UserLookUp,
    AddShiftForm,
    AddRecurringShiftForm,
)

from SIs.models import (
    SIRoleInfo,
)

from tutors.models import (
    TutorRoleInfo,
)

from . import (
    get_color_coder_dict,
    color_coder,
)

def schedule_for_all_course_for_start(request, start_date, shift_kind, remove_empty = False):
    # Optimize: Get active semester once
    active_semester = Semester.objects.get_active_semester()
    
    # Optimize: Use select_related to avoid N+1 queries
    filtered_shift = Shift.objects.select_related(
        'position', 'position__user', 'building'
    ).filter(
        Q(start__date__gte = start_date) & Q(start__date__lte = (start_date + timedelta(days=6))) & Q(kind__in = shift_kind)
    ).order_by("start")   
    
    # Optimize: Get all SI and tutor roles with select_related
    filtered_si_role = SIRoleInfo.objects.select_related(
        'position', 'position__user', 'assigned_class', 'assigned_class__course'
    ).filter(position__semester = active_semester)
    
    filtered_tutor_role = TutorRoleInfo.objects.select_related(
        'position', 'position__user'
    ).prefetch_related('assigned_courses').filter(
        position__semester = active_semester
    )
    
    # Optimize: Get courses with related data
    courses = Course.objects.select_related('subject').all()
    
    # Optimize: Build position mappings in bulk
    si_course_positions = {}
    for role in filtered_si_role:
        if role.assigned_class is not None:
            course = role.assigned_class.course
            if course not in si_course_positions:
                si_course_positions[course] = set()
            si_course_positions[course].add(role.position_id)
    
    tutor_course_positions = {}
    for role in filtered_tutor_role:
        for course in role.assigned_courses.all():
            if course not in tutor_course_positions:
                tutor_course_positions[course] = set()
            tutor_course_positions[course].add(role.position_id)
    
    # Optimize: Group shifts by position for faster lookup
    shifts_by_position = {}
    for shift in filtered_shift:
        if shift.position_id not in shifts_by_position:
            shifts_by_position[shift.position_id] = []
        shifts_by_position[shift.position_id].append(shift)
    
    schedule = {}
    
    for course in courses:
        shifts_info = [[], [], [], [], [], [], []]
        
        # Get all positions for this course
        course_positions = set()
        course_positions.update(si_course_positions.get(course, set()))
        course_positions.update(tutor_course_positions.get(course, set()))
        
        # Get all shifts for these positions
        for position_id in course_positions:
            for shift in shifts_by_position.get(position_id, []):
                index = (timezone.localtime(shift.start).date() - start_date).days
                if 0 <= index <= 6:
                    shifts_info[index].append(shift)

        schedule[str(course)] = shifts_info
        
        if remove_empty and sum([len(shifts_info[i]) for i in range(7)]) == 0:
            schedule.pop(str(course))
    
    return schedule

@login_required
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def schedule_for_all_course(request):
    start_date = timezone.localtime(timezone.now()).date()
    context = {
        "colors": get_color_coder_dict(),
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": schedule_for_all_course_for_start(request, start_date, [ShiftKind.SI_SESSION, ShiftKind.TUTOR_DROP_IN, ShiftKind.TUTOR_APPOINTMENT]),
    }
    return render(request, "schedule_all_courses.html", context)