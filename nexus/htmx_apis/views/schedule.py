from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.views import restrict_to_http_methods, restrict_to_groups


from shifts.models import (
    ShiftKind,
)

from shifts.views.schedule import (
    schedule_for_all_course_for_start,
)

from shifts.views import (
    get_color_coder_dict,
)

@restrict_to_http_methods("GET")
def api_si_schedule_for_all_course(request):
    start_date = timezone.localtime(timezone.now()).date()
    context = {
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": schedule_for_all_course_for_start(request, start_date, [ShiftKind.SI_SESSION], True),
    }
    return render(request, "api_schedule.html", context)

@restrict_to_http_methods("GET")
def api_tutor_schedule_for_all_course(request):
    start_date = timezone.localtime(timezone.now()).date()
    context = {
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": schedule_for_all_course_for_start(request, start_date, [ShiftKind.TUTOR_DROP_IN], True),
    }
    return render(request, "api_schedule.html", context)