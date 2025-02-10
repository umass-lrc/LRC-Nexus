from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.cache import cache_page

from core.views import restrict_to_http_methods, restrict_to_groups


from shifts.models import (
    ShiftKind,
)

from SIs.models import (
    SIRoleInfo,
)

from shifts.views.schedule import (
    schedule_for_all_course_for_start,
)

from shifts.views import (
    get_color_coder_dict,
)

# @cache_page(60 * 60)
@restrict_to_http_methods("GET")
def api_si_schedule_for_all_course(request):
    start_date = timezone.localtime(timezone.now()).date()
    si_schedule = schedule_for_all_course_for_start(request, start_date, [ShiftKind.SI_SESSION], True)
    for course, days in si_schedule.items():
        for i, day in enumerate(days):
            new_day = []
            for shift in day:
                role = SIRoleInfo.objects.get(position=shift.position)
                faculty = role.assigned_class.faculty if not role.all_sections else "All Sections"
                new_day.append((shift, faculty))
            si_schedule[course][i] = new_day
    context = {
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": si_schedule,
    }
    return render(request, "api_schedule_si.html", context)

# @cache_page(60 * 60)
@restrict_to_http_methods("GET")
def api_tutor_schedule_for_all_course(request):
    start_date = timezone.localtime(timezone.now()).date()
    tutor_schedule = schedule_for_all_course_for_start(request, start_date, [ShiftKind.TUTOR_DROP_IN], True)
    for course, days in tutor_schedule.items():
        for i, day in enumerate(days):
            day_time_coverage = []
            for shift in day:
                if len(day_time_coverage) != 0 and shift.original_start <= day_time_coverage[-1]['end']:
                    day_time_coverage[-1]['end'] = max(day_time_coverage[-1]['end'], shift.original_start + shift.original_duration)
                else:
                    day_time_coverage.append({
                        'start': shift.original_start,
                        'end': shift.original_start + shift.original_duration,
                    })
            tutor_schedule[course][i] = day_time_coverage
    context = {
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": tutor_schedule,
        "kind": ShiftKind.TUTOR_DROP_IN,
    }
    return render(request, "api_schedule_tutor.html", context)