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

@login_required
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def schedule_for_all_course_for_start(request, start_date):
    positions = Positions.objects.filter(
        semester = Semester.objects.get_active_semester()
    )
    
    courses = Course.objects.all()
    
    schedule = {}
    
    for course in courses:
        shifts_info = [[], [], [], [], [], [], []]
        
        si_positions = SIRoleInfo.objects.filter(
            assigned_class__course = course,
        ).values_list("position", flat=True).distinct()
        
        tutor_positions = TutorRoleInfo.objects.filter(
            assigned_courses__in = [course],
        ).values_list("position", flat=True).distinct()
        
        Shifts = Shift.objects.filter(
            Q(position__in = si_positions) | Q(position__in = tutor_positions),
            Q(start__date__gte = start_date) & Q(start__date__lte = start_date + timedelta(days=6)),
            Q(kind = ShiftKind.SI_SESSION) | Q(kind = ShiftKind.TUTOR_DROP_IN) | Q(kind = ShiftKind.TUTOR_APPOINTMENT),
        ).order_by("start")

        for shift in Shifts:
            index = (shift.start.date() - start_date).days
            if index > 6:
                continue
            shifts_info[index].append(shift)

        schedule[str(course)] = shifts_info
    
    return schedule

@login_required
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def schedule_for_all_course(request):
    start_date = timezone.now().date()
    context = {
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": schedule_for_all_course_for_start(request, start_date),
    }
    return render(request, "schedule_all_courses.html", context)