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

from tutors.models import (
    TutorRoleInfo,
)

from core.models import (
    Course,
    Semester,
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

@restrict_to_http_methods("GET")
def api_tutor_schedule_for_all_course(request):
    start_date = timezone.localtime(timezone.now()).date()
    end_date = start_date + timedelta(days=6)

    # Build schedule per course using direct per-course role filtering (mirrors previous working logic)
    active_semester = Semester.objects.get_active_semester()
    courses = Course.objects.select_related('subject').all()
    tutor_schedule = {}

    # Prefetch roles once for performance
    all_roles = TutorRoleInfo.objects.select_related('position').prefetch_related('assigned_courses').filter(position__semester=active_semester)

    # Build cross-listing family map
    course_id_to_main_id = {}
    main_to_all_ids = {}
    for c in courses:
        main_id = c.main_course_id if c.is_cross_listed and c.main_course_id else c.id
        course_id_to_main_id[c.id] = main_id
        if main_id not in main_to_all_ids:
            main_to_all_ids[main_id] = set()
        main_to_all_ids[main_id].add(c.id)

    for c in courses:
        course_key = str(c)
        days = [[], [], [], [], [], [], []]
        main_id = course_id_to_main_id.get(c.id, c.id)
        family_ids = list(main_to_all_ids.get(main_id, {c.id}))

        # Get positions for roles assigned to any course in this family
        role_positions = set(
            all_roles.filter(assigned_courses__in=family_ids).values_list('position_id', flat=True).distinct()
        )

        if not role_positions:
            continue

        # Fetch this week's drop-in shifts for those positions
        from shifts.models import Shift  # local import to avoid circular
        weekly_shifts = (
            Shift.objects.select_related('position')
            .filter(
                position_id__in=role_positions,
                kind=ShiftKind.TUTOR_DROP_IN,
                dropped=False,
                start__date__gte=start_date,
                start__date__lte=end_date,
            )
            .order_by('start')
        )

        # Transform into time coverage per day
        for shift in weekly_shifts:
            di = (timezone.localtime(shift.start).date() - start_date).days
            if 0 <= di <= 6:
                shift_start = shift.original_start if shift.original_start is not None else shift.start
                shift_duration = shift.original_duration if shift.original_duration is not None else shift.duration
                slots = days[di]
                if slots and shift_start <= slots[-1]['end']:
                    slots[-1]['end'] = max(slots[-1]['end'], shift_start + shift_duration)
                else:
                    slots.append({'start': shift_start, 'end': shift_start + shift_duration})

        # Only include non-empty courses
        if any(len(days[i]) for i in range(7)):
            tutor_schedule[course_key] = days
    context = {
        "dates": [start_date + timedelta(days=i) for i in range(7)],
        "schedule": tutor_schedule,
        "kind": ShiftKind.TUTOR_DROP_IN,
    }
    return render(request, "api_schedule_tutor.html", context)