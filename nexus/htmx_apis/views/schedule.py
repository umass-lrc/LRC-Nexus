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

# @cache_page(60 * 15)  # Cache for 15 minutes
@restrict_to_http_methods("GET")
def api_si_schedule_for_all_course(request):
    start_date = timezone.localtime(timezone.now()).date()
    si_schedule = schedule_for_all_course_for_start(request, start_date, [ShiftKind.SI_SESSION], True)
    
    # Optimize: Get all SI roles in bulk to avoid N+1 queries
    all_positions = set()
    for course, days in si_schedule.items():
        for day in days:
            for shift in day:
                all_positions.add(shift.position_id)
    
    # Bulk fetch all SI role info
    si_roles_dict = {}
    if all_positions:
        si_roles = SIRoleInfo.objects.select_related(
            'position', 'assigned_class', 'assigned_class__faculty'
        ).filter(position_id__in=all_positions)
        
        for role in si_roles:
            si_roles_dict[role.position_id] = role
    
    # Process schedule with bulk-loaded data
    for course, days in si_schedule.items():
        for i, day in enumerate(days):
            new_day = []
            for shift in day:
                role = si_roles_dict.get(shift.position_id)
                if role:
                    faculty = role.assigned_class.faculty if not role.all_sections else "All Sections"
                    new_day.append((shift, faculty))
                else:
                    new_day.append((shift, "Unknown"))
            si_schedule[course][i] = new_day
            
    context = {
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": si_schedule,
    }
    return render(request, "api_schedule_si.html", context)

# @cache_page(60 * 15)  # Cache for 15 minutes
@restrict_to_http_methods("GET")
def api_tutor_schedule_for_all_course(request):
    start_date = timezone.localtime(timezone.now()).date()
    tutor_schedule = schedule_for_all_course_for_start(request, start_date, [ShiftKind.TUTOR_DROP_IN], True)
    
    for course, days in tutor_schedule.items():
        for i, day in enumerate(days):
            day_time_coverage = []
            for shift in day:
                shift_start = shift.original_start if shift.original_start is not None else shift.start
                shift_duration = shift.original_duration if shift.original_duration is not None else shift.duration
                
                # Duration is now stored as timedelta directly (PostgreSQL INTERVAL type)
                if len(day_time_coverage) != 0 and shift_start <= day_time_coverage[-1]['end']:
                    day_time_coverage[-1]['end'] = max(day_time_coverage[-1]['end'], shift_start + shift_duration)
                else:
                    day_time_coverage.append({
                        'start': shift_start,
                        'end': shift_start + shift_duration,
                    })
            tutor_schedule[course][i] = day_time_coverage
    context = {
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": tutor_schedule,
        "kind": ShiftKind.TUTOR_DROP_IN,
    }
    return render(request, "api_schedule_tutor.html", context)