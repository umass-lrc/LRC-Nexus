from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

from core.views import restrict_to_http_methods, restrict_to_groups

from shifts.models import (
    State,
    ChangeRequest,
    DropRequest,
)

from users.models import (
    PositionChoices,
)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def shift_requests(request):
    context = {
        'position': 'Tutors',
        'state': State,
        'change_url_name': 'tutor_change_request',
        'drop_url_name': 'tutor_drop_request',
    }
    return render(request, "shift_request_main.html", context)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def change_request(request, request_state):
    requests = ChangeRequest.objects.filter(
        Q(state = request_state) & (Q(shift__position__position = PositionChoices.TUTOR) | Q(shift__position__position = PositionChoices.TUTOR_PM) | Q(position__position = PositionChoices.TUTOR) | Q(position__position = PositionChoices.TUTOR_PM)),
    ).order_by('start')
    context = {
        'c_requests': requests,
    }
    return render(request, "shift_request_change_table.html", context)


@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def drop_request(request, request_state):
    requests = DropRequest.objects.filter(
        Q(state = request_state) & (Q(shift__position__position = PositionChoices.TUTOR) | Q(shift__position__position = PositionChoices.TUTOR_PM)),
    ).order_by('shift__start')
    context = {
        'c_requests': requests,
    }
    return render(request, "shift_request_drop_table.html", context)