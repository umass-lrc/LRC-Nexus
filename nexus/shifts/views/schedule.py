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
    filtered_shift = Shift.objects.filter(
        Q(start__date__gte = start_date) & Q(start__date__lte = (start_date + timedelta(days=6))) & Q(kind__in = shift_kind)
    ).order_by("start")   
    
    filtered_si_role = SIRoleInfo.objects.filter(
        position__semester = Semester.objects.get_active_semester(),
    )
    
    filtered_tutor_role = TutorRoleInfo.objects.filter(
        position__semester = Semester.objects.get_active_semester(),
    )
    
    courses = Course.objects.all()
    
    schedule = {}
    
    for course in courses:
        shifts_info = [[], [], [], [], [], [], []]
        
        si_positions = filtered_si_role.filter(
            assigned_class__course = course,
        ).values_list("position", flat=True).distinct()
        
        tutor_positions = filtered_tutor_role.filter(
            assigned_courses__in = [course],
        ).values_list("position", flat=True).distinct()
        
        Shifts = filtered_shift.filter(
            Q(position__in = si_positions) | Q(position__in = tutor_positions)
        )

        for shift in Shifts:
            index = (timezone.localtime(shift.start).date() - start_date).days
            if index < 0 or index > 6:
                continue
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