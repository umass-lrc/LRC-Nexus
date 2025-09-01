from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.views import restrict_to_http_methods, restrict_to_groups


from shifts.models import (
    AttendanceInfo,
)

from core.models import (
    Semester
)

from users.models import (
    PositionChoices
)

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    return hours, minutes

@login_required
@restrict_to_groups("Staff Admin", "Tutor Supervisor")
@restrict_to_http_methods("GET")
def live_punch_in_out(request):
    punched_in = AttendanceInfo.objects.filter(
        shift__position__position__in=[PositionChoices.TUTOR, PositionChoices.TUTOR_PM, PositionChoices.GRADUATE_TUTOR],
        shift__position__semester = Semester.objects.get_active_semester(), 
        punch_in_time__isnull=False, 
        punch_out_time__isnull=True,
    ).values_list("id", flat=True)

    context = {
        'punched_in': punched_in,
    }
    return render(request, "live_punch_in_out_main.html", context=context)

@login_required
@restrict_to_groups("Staff Admin", "Tutor Supervisor")
@restrict_to_http_methods("GET")
def get_punched_in(request, id):
    att_info = AttendanceInfo.objects.get(id=id)
    hours, minutes = convert_timedelta(timezone.now() - att_info.shift.start)
    context = {
        'id': att_info.id,
        'name': str(att_info.shift.position.user),
        'position': att_info.shift.position.get_position_display(),
        'kind': att_info.shift.kind,
        'duration': f"{hours:02d}:{minutes:02d}",
    }
    return render(request, "punched_in_row.html", context=context)