from datetime import timedelta
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

from ..forms.shift_request import (
    AddRequestForm,
    ChangeRequestForm,
)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def shift_requests(request):
    context = {
        'position': 'SIs',
        'state': State,
        'change_url_name': 'si_change_request',
        'drop_url_name': 'si_drop_request',
        'add_url_name': 'si_add_request',
    }
    return render(request, "shift_request_main.html", context)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def add_request(request, request_state):
    requests = ChangeRequest.objects.filter(
        Q(state = request_state) & (Q(position__position = PositionChoices.SI) | Q(position__position = PositionChoices.SI_PM)),
    ).order_by('start')
    context = {
        'a_requests': requests,
        'url_name': 'si_add_request_form',
    }
    return render(request, "shift_request_add_table.html", context)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def change_request(request, request_state):
    requests = ChangeRequest.objects.filter(
        Q(state = request_state) & (Q(shift__position__position = PositionChoices.SI) | Q(shift__position__position = PositionChoices.SI_PM)),
    ).order_by('start')
    context = {
        'c_requests': requests,
        'url_name': 'si_change_request_form',
    }
    return render(request, "shift_request_change_table.html", context)


@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def drop_request(request, request_state):
    requests = DropRequest.objects.filter(
        state = request_state,
        shift__position__position = PositionChoices.SI,
    ).order_by('shift__start')
    context = {
        'd_requests': requests,
        'url_name': 'si_drop_request_form',
    }
    return render(request, "shift_request_drop_table.html", context)

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def add_request_form(request, req_id):
    arequest = ChangeRequest.objects.get(id=req_id)
    state = arequest.state
    response = None
    if state == State.APPROVED or state == State.DENIED:
        response = render(request, "add_request_details.html", {"add_request": arequest})
    elif state == State.NOT_VIEWED:
        if request.method == "POST":
            res_type = request.POST.get('type')
            if res_type == "deny":
                arequest.state = State.DENIED
                arequest.last_changed_on = timezone.now()
                arequest.last_change_by = request.user
                arequest.save()
                messages.success(request, "Request Denied")
                response = render(request, "add_request_response.html")
            elif res_type == "in_progress":
                arequest.state = State.IN_PROGRESS
                arequest.last_changed_on = timezone.now()
                arequest.last_change_by = request.user
                arequest.save()
                messages.success(request, "Request Moved to In Progress")
                response = render(request, "add_request_response.html")
            response['HX-Trigger-After-Settle'] = json.dumps({"stateChanged": f"art-{req_id}"})
            return response
        context = {
            'req_id': req_id,
            'url_name': 'si_add_request_form',
            'add_request': arequest,  
        }
        response = render(request, "add_request_not_viewed.html", context)
    else:
        if request.method == "POST":
            form = AddRequestForm(request.POST, instance=arequest)
            if request.POST.get('deney', None) is not None:
                arequest.state = State.DENIED
                arequest.last_changed_on = timezone.now()
                arequest.last_change_by = request.user
                arequest.save()
                messages.success(request, "Request Denied")
                response = render(request, "add_request_response.html")
            elif not form.is_valid():
                messages.error(request, f"Form Errors: {form.errors}")
                context = {
                    "add_request": arequest,
                    "url_name": "si_add_request_form",
                }
                return render(request, "add_request_update_response.html", context)
            else:
                data = form.cleaned_data
                arequest.position = data['position']
                arequest.start = data['start']
                arequest.duration = timedelta(hours=data['hours'], minutes=data['minutes'])
                arequest.building = data['building']
                arequest.room = data['room']
                arequest.kind = data['kind']
                arequest.require_punch_in_out = data['require_punch_in_out']
                arequest.last_changed_on = timezone.now()
                arequest.last_change_by = request.user
                if request.POST.get('update_and_approve', None) is not None:
                    arequest.save()
                    arequest.change_status_to_approved(request.user)
                    messages.success(request, "Request Updated and Approved")
                    response = render(request, "add_request_response.html")
                else:
                    arequest.save()
                    messages.success(request, "Request Updated")
                    context = {
                        "add_request": arequest,
                        "url_name": "si_add_request_form",
                    }
                    return render(request, "add_request_update_response.html", context)
            response['HX-Trigger-After-Settle'] = json.dumps({"stateChanged": f"art-{req_id}"})
            return response
        context = {
            'form': AddRequestForm(instance=arequest),
            'add_request': arequest,
        }
        response = render(request, "just_form.html", context)
    response["HX-Trigger-After-Settle"] = json.dumps({"requestClicked": f"art-{req_id}"})
    return response

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def change_request_form(request, req_id):
    crequest = ChangeRequest.objects.get(id=req_id)
    state = crequest.state
    response = None
    if state == State.APPROVED or state == State.DENIED:
        response = render(request, "change_request_details.html", {"change_request": crequest})
    elif state == State.NOT_VIEWED:
        if request.method == "POST":
            res_type = request.POST.get('type')
            if res_type == "deny":
                crequest.state = State.DENIED
                crequest.last_changed_on = timezone.now()
                crequest.last_change_by = request.user
                crequest.save()
                messages.success(request, "Request Denied")
                response = render(request, "change_request_response.html")
            elif res_type == "in_progress":
                crequest.state = State.IN_PROGRESS
                crequest.last_changed_on = timezone.now()
                crequest.last_change_by = request.user
                crequest.save()
                messages.success(request, "Request Moved to In Progress")
                response = render(request, "change_request_response.html")
            response['HX-Trigger-After-Settle'] = json.dumps({"stateChanged": f"crt-{req_id}"})
            return response
        context = {
            'req_id': req_id,
            'url_name': 'si_change_request_form',
            'change_request': crequest,  
        }
        response = render(request, "change_request_not_viewed.html", context)
    else:
        if request.method == "POST":
            form = ChangeRequestForm(request.POST, instance=crequest)
            if request.POST.get('deney', None) is not None:
                crequest.state = State.DENIED
                crequest.last_changed_on = timezone.now()
                crequest.last_change_by = request.user
                crequest.save()
                messages.success(request, "Request Denied")
                response = render(request, "add_request_response.html")
            elif not form.is_valid():
                messages.error(request, f"Form Errors: {form.errors}")
                context = {
                    "add_request": crequest,
                    "url_name": "si_change_request_form",
                }
                return render(request, "change_request_update_response.html", context)
            else:
                data = form.cleaned_data
                crequest.position = data['position']
                crequest.start = data['start']
                crequest.duration = timedelta(hours=data['hours'], minutes=data['minutes'])
                crequest.building = data['building']
                crequest.room = data['room']
                crequest.kind = data['kind']
                crequest.require_punch_in_out = data['require_punch_in_out']
                crequest.last_changed_on = timezone.now()
                crequest.last_change_by = request.user
                if request.POST.get('update_and_approve', None) is not None:
                    crequest.save()
                    crequest.change_status_to_approved(request.user)
                    messages.success(request, "Request Updated and Approved")
                    response = render(request, "add_request_response.html")
                else:
                    crequest.save()
                    messages.success(request, "Request Updated")
                    context = {
                        "change_request": crequest,
                        "url_name": "si_change_request_form",
                    }
                    return render(request, "change_request_update_response.html", context)
            response['HX-Trigger-After-Settle'] = json.dumps({"stateChanged": f"crt-{req_id}"})
            return response
        context = {
            'form': ChangeRequestForm(instance=crequest),
            'change_request': crequest,
        }
        response = render(request, "just_form.html", context)
    response["HX-Trigger-After-Settle"] = json.dumps({"requestClicked": f"crt-{req_id}"})
    return response

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor")
def drop_request_form(request, req_id):
    drequest = DropRequest.objects.get(id=req_id)
    state = drequest.state
    response = None
    if state == State.APPROVED or state == State.DENIED:
        response = render(request, "drop_request_details.html", {"drop_request": drequest})
    elif state == State.NOT_VIEWED:
        if request.method == "POST":
            res_type = request.POST.get('type')
            if res_type == "deny":
                drequest.change_status_to_denied(request.user)
                messages.success(request, "Request Denied")
                response = render(request, "drop_request_response.html")
            elif res_type == "approve":
                drequest.change_status_to_approved(request.user)
                messages.success(request, "Request Approved")
                response = render(request, "drop_request_response.html")
            response['HX-Trigger-After-Settle'] = json.dumps({"stateChanged": f"drt-{req_id}"})
            return response
        context = {
            'req_id': req_id,
            'url_name': 'si_drop_request_form',
            'drop_request': drequest,  
        }
        response = render(request, "drop_request_not_viewed.html", context)
    response["HX-Trigger-After-Settle"] = json.dumps({"requestClicked": f"drt-{req_id}"})
    return response