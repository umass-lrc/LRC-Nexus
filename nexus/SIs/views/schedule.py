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


from shifts.models import (
    ShiftKind,
)

from shifts.views.schedule import (
    schedule_for_all_course_for_start,
)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def si_schedule_for_all_course(request):
    start_date = timezone.localtime(timezone.now()).date()
    context = {
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": schedule_for_all_course_for_start(request, start_date, [ShiftKind.SI_SESSION, ShiftKind.CLASS], True),
    }
    return render(request, "schedule_all_courses.html", context)