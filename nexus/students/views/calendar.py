from datetime import datetime, timedelta
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from django.db.models import Q

from dal import autocomplete

from core.views import restrict_to_http_methods, restrict_to_groups

from users.models import (
    Positions,
    PositionChoices,
    NexusUser,
)

from core.models import (
    Semester,
)

from shifts.models import (
    AttendanceInfo,
    Shift,
    State,
    ChangeRequest,
    DropRequest,
    ShiftKind,
)

from ..forms.calendar import (
    AddShiftRequestForm,
    ChangeShiftRequestForm,
    DropShiftRequestForm,
)

from shifts.views import (
    get_color_coder_dict,
    color_coder,
)

@login_required
@restrict_to_http_methods('GET')
def student_calendar(request):
    return render(request, 'student_calander.html')

@login_required
@restrict_to_http_methods("GET")
def get_student_calendar(request):
    response = render(request, "color_coder.html", {'colors': get_color_coder_dict()})
    response["HX-Trigger-After-Settle"] = "calendar"
    return response

@login_required
@restrict_to_http_methods("GET")
def get_student_shifts(request):
    user = request.user
    start = datetime.fromisoformat(request.GET["start"])
    end = datetime.fromisoformat(request.GET["end"])
    
    events_data = []
    
    shifts = Shift.objects.filter(position__user=user, start__gte=start, start__lte=end).all()
    change_shifts = ChangeRequest.objects.filter(Q(shift__isnull=False) & Q(shift__position__user=user) & Q(state__in=[State.IN_PROGRESS, State.NOT_VIEWED]) & ((Q(start__gte=start) & Q(start__lte=end)) | (Q(shift__start__gte=start) & Q(shift__start__lte=end)))).all()
    add_req = ChangeRequest.objects.filter(shift__isnull=True, position__user=user, start__gte=start, start__lte=end, state__in=[State.IN_PROGRESS, State.NOT_VIEWED]).all()
    drop_shifts = DropRequest.objects.filter(shift__position__user=user, shift__start__gte=start, shift__start__lte=end, state__in=[State.IN_PROGRESS, State.NOT_VIEWED]).all()
    for shift in shifts:
        if change_shifts.filter(shift=shift).exists() or drop_shifts.filter(shift=shift).exists():
            continue
        if timezone.now()> timezone.localtime(shift.start + shift.duration) and shift.attendance_info.attended == False:
            title = f"""
                <s style='background-color: #D3D3D3;'>{str(shift)}</s>
            """
            event_color = '#808080'
        else:
            title = str(shift)
            event_color = color_coder(shift.kind)
        description = f"""
            <b>{shift.kind}</b>
            <hr/>
            <b>Start:</b> {timezone.localtime(shift.start).strftime("%-I:%M %p")}<br/>
            <b>End:</b> {timezone.localtime(shift.start + shift.duration).strftime("%-I:%M %p")}<br/>
            <b>Location:</b> {shift.building.short_name}-{shift.room}
            <hr/>
            <b>Attended?</b> {shift.attendance_info.attended}<br/>
            <b>Signed?</b> {shift.attendance_info.signed}
        """
        events_data.append({
            "id": str(shift.id),
            "start": shift.start.isoformat(),
            "end": (shift.start + shift.duration).isoformat(),
            "title": title,
            "allDay": False,
            "color": event_color,
            "extendedProps": {
                "url": reverse("change_or_drop_shift_request", kwargs={"shift_id": shift.id}),
                "description": description,
            }
        })
    
    for req in change_shifts:
        shift = req.shift
        description1 = f"""
            <b>Change Request: {req.kind} - {req.position}</b>
            <hr/>
            <b>Start:</b> {timezone.localtime(req.start).strftime("%-I:%M %p")}<br/>
            <b>End:</b> {timezone.localtime(req.start + req.duration).strftime("%-I:%M %p")}<br/>
            <b>Location:</b> {req.building.short_name}-{req.room}
            <hr/>
            <b>State?</b> {req.state}<br/>
            <b>Last Change By?</b> {req.last_change_by}<br/>
            <hr/>
            <b>Click on the shift to know more about the change request</b>
        """
        description2 = f"""
            <b>Change Request: {shift.kind} -> {req.kind}</b>
            <hr/>
            <b>Start:</b> {timezone.localtime(shift.start).strftime("%-I:%M %p")}<br/>
            <b>End:</b> {timezone.localtime(shift.start + shift.duration).strftime("%-I:%M %p")}<br/>
            <b>Location:</b> {shift.building.short_name}-{shift.room}
            <hr/>
            <b>Click on the shift to know more about the change request</b>
        """
        events_data.append({
            "id": f"req-{req.id}",
            "start": req.start.isoformat(),
            "end": (req.start + req.duration).isoformat(),
            "title": f"Requested: {req.kind} - {req.position}",
            "allDay": False,
            "color": color_coder(req.kind),
            "textColor": "#FFA500",
            "extendedProps": {
                "url": reverse("change_or_drop_shift_request", kwargs={"shift_id": shift.id}),
                "description": description1,
            }
        })
        events_data.append({
            "id": f"{shift.id}",
            "start": shift.start.isoformat(),
            "end": (shift.start + shift.duration).isoformat(),
            "title": f"Drop Requested: {shift.kind} - {shift.position}",
            "allDay": False,
            "color": color_coder(shift.kind),
            "textColor": "#FFA500",
            "extendedProps": {
                "url": reverse("change_or_drop_shift_request", kwargs={"shift_id": shift.id}),
                "description": description2,
            }
        })
    
    for req in drop_shifts:
        shift = req.shift
        description = f"""
            <b>Drop Request: {shift.kind}</b>
            <hr/>
            <b>Start:</b> {timezone.localtime(shift.start).strftime("%-I:%M %p")}<br/>
            <b>End:</b> {timezone.localtime(shift.start + shift.duration).strftime("%-I:%M %p")}<br/>
            <b>Location:</b> {shift.building.short_name}-{shift.room}
            <hr/>
            <b>Click on the shift to know more about the drop request</b>
        """
        events_data.append({
            "id": f"{shift.id}",
            "start": shift.start.isoformat(),
            "end": (shift.start + shift.duration).isoformat(),
            "title": f"Drop Rquested: {shift.kind} - {shift.position}",
            "allDay": False,
            "color": color_coder(shift.kind),
            "textColor": "#FFA500",
            "extendedProps": {
                "url": reverse("change_or_drop_shift_request", kwargs={"shift_id": shift.id}),
                "description": description,
            }
        })
    
    for req in add_req:
        description = f"""
            <b>Add Request: {req.kind} - {req.position}</b>
            <hr/>
            <b>Start:</b> {timezone.localtime(req.start).strftime("%-I:%M %p")}<br/>
            <b>End:</b> {timezone.localtime(req.start + req.duration).strftime("%-I:%M %p")}<br/>
            <b>Location:</b> {req.building.short_name}-{req.room}
            <hr/>
            <b>State?</b> {req.state}<br/>
            <b>Last Change By?</b> {req.last_change_by}<br/>
        """
        events_data.append({
            "id": f"req-{req.id}",
            "start": req.start.isoformat(),
            "end": (req.start + req.duration).isoformat(),
            "title": f"Requested: {req.kind} - {req.position}",
            "allDay": False,
            "color": color_coder(req.kind),
            "textColor": "#FFA500",
            "extendedProps": {
                "url": reverse("add_shift_request_display", kwargs={"req_id": req.id}),
                "description": description,
            }
        })
    
    return JsonResponse(events_data, safe=False)


@login_required
@restrict_to_http_methods("GET", "POST")
def add_shift_request(request):
    if request.method == "POST":
        form = AddShiftRequestForm(request.user, request.POST)
        if not form.is_valid():
            messages.error(request, f"Form Error: {form.errors}")
            return render(request, "add_shift_req_response.html", {"success": False})
        data = form.cleaned_data
        if (data["kind"] == ShiftKind.SI_SESSION or data["kind"] == ShiftKind.CLASS) and data["start"] - timezone.now() < timedelta(days=7):
            messages.error(request, f"Add Request for SI Session or Class must be made 7 days before the shift.")
            return render(request, "add_shift_req_response.html", {"si_lock": True})
        req = ChangeRequest.objects.create(
            position=data["position"],
            start=data["start"],
            duration=timedelta(hours=data["hours"], minutes=data["minutes"]),
            building=data["building"],
            room=data["room"],
            kind=data["kind"],
            reason=data["reason"],
            state=State.NOT_VIEWED,
        )
        messages.success(request, "Shift Successfully Requested.")
        response = render(request, "add_shift_req_response.html", {"success": True})
        description = f"""
            <b>Add Request: {req.kind} - {req.position}</b>
            <hr/>
            <b>Start:</b> {timezone.localtime(req.start).strftime("%-I:%M %p")}<br/>
            <b>End:</b> {timezone.localtime(req.start + req.duration).strftime("%-I:%M %p")}<br/>
            <b>Location:</b> {req.building.short_name}-{req.room}
            <hr/>
            <b>State?</b> {req.state}<br/>
            <b>Last Change By?</b> {req.last_change_by}<br/>
            <hr/>
            <b>Click on the shift to know more about the add request</b>
        """
        response["HX-Trigger-After-Settle"] = json.dumps({
            "addShiftRequest": json.dumps({
                "id": f"req-{req.id}",
                "start": req.start.isoformat(),
                "end": (req.start + req.duration).isoformat(),
                "title": f"Requested: {req.kind} - {req.position}",
                "allDay": False,
                "color": color_coder(req.kind),
                "textColor": "#FFA500",
                "extendedProps": {
                    "url": reverse("add_shift_request_display", kwargs={"req_id": req.id}),
                    "description": description,
                }
            })
        })
        return response
    form = AddShiftRequestForm(request.user)
    return render(request, "just_form.html", {"form": form})

@login_required
@restrict_to_http_methods("GET")
def add_shift_request_display(request, req_id):
    req = ChangeRequest.objects.get(id=req_id)
    context = {"can_make_request": False, "add_request": req}
    return render(request, "change_or_drop_shift_request.html", context)

@login_required
@restrict_to_http_methods("GET")
def change_or_drop_shift_request(request, shift_id):
    change_request = ChangeRequest.objects.filter(shift__id=shift_id).first()
    drop_request = DropRequest.objects.filter(shift__id=shift_id).first()
    can_make_request = change_request is None and drop_request is None
    context = {"can_make_request": can_make_request, "shift_id": shift_id}
    if change_request is not None:
        req = ChangeRequest.objects.get(shift__id=shift_id)
        context["change_request"] = req
    elif drop_request is not None:
        req = DropRequest.objects.get(shift__id=shift_id)
        context["drop_request"] = req
    return render(request, "change_or_drop_shift_request.html", context)

@login_required
@restrict_to_http_methods("GET", "POST")
def change_shift_request(request, shift_id):
    shift = Shift.objects.get(id=shift_id)
    if request.method == "POST":
        form = ChangeShiftRequestForm(shift, request.POST)
        if not form.is_valid():
            messages.error(request, f"Form Error: {form.errors}")
            return render(request, "change_or_drop_shift_req_response.html", {"success": False})
        data = form.cleaned_data
        req = ChangeRequest.objects.create(
            shift=shift,
            start=data["start"],
            duration=timedelta(hours=data["hours"], minutes=data["minutes"]),
            building=data["building"],
            room=data["room"],
            kind=data["kind"],
            reason=data["reason"],
            state=State.NOT_VIEWED,
        )
        messages.success(request, "Shift Change Successfully Requested.")
        response = render(request, "change_or_drop_shift_req_response.html", {"success": True, "shift_id": shift_id})
        description1 = f"""
            <b>Change Request: {req.kind} - {req.position}</b>
            <hr/>
            <b>Start:</b> {timezone.localtime(req.start).strftime("%-I:%M %p")}<br/>
            <b>End:</b> {timezone.localtime(req.start + req.duration).strftime("%-I:%M %p")}<br/>
            <b>Location:</b> {req.building.short_name}-{req.room}
            <hr/>
            <b>State?</b> {req.state}<br/>
            <b>Last Change By?</b> {req.last_change_by}<br/>
            <hr/>
            <b>Click on the shift to know more about the change request</b>
        """
        description2 = f"""
            <b>Change Request: {shift.kind} -> {req.kind}</b>
            <hr/>
            <b>Start:</b> {timezone.localtime(shift.start).strftime("%-I:%M %p")}<br/>
            <b>End:</b> {timezone.localtime(shift.start + shift.duration).strftime("%-I:%M %p")}<br/>
            <b>Location:</b> {shift.building.short_name}-{shift.room}
            <hr/>
            <b>Click on the shift to know more about the change request</b>
        """
        response["HX-Trigger-After-Settle"] = json.dumps({
            "addShiftRequest": json.dumps({
                "id": f"req-{req.id}",
                "start": req.start.isoformat(),
                "end": (req.start + req.duration).isoformat(),
                "title": f"Requested: {req.kind} - {req.position}",
                "allDay": False,
                "color": color_coder(req.kind),
                "textColor": "#FFA500",
                "extendedProps": {
                    "url": reverse("change_or_drop_shift_request", kwargs={"shift_id": shift.id}),
                    "description": description1,
                }
            }),
            "editShift": json.dumps({
                "id": f"{shift.id}",
                "start": shift.start.isoformat(),
                "end": (shift.start + shift.duration).isoformat(),
                "title": f"Drop Rquested: {shift.kind} - {shift.position}",
                "allDay": False,
                "color": color_coder(shift.kind),
                "textColor": "#FFA500",
                "extendedProps": {
                    "url": reverse("change_or_drop_shift_request", kwargs={"shift_id": shift.id}),
                    "description": description2,
                }
            }),
        })
        return response
    if (shift.kind == ShiftKind.SI_SESSION or shift.kind == ShiftKind.CLASS) and shift.start - timezone.now() < timedelta(days=7):
        return render(request, "si_directions_7_days.html")
    form = ChangeShiftRequestForm(shift)
    return render(request, "just_form.html", {"form": form})

@login_required
@restrict_to_http_methods("GET", "POST")
def drop_shift_request(request, shift_id):
    shift = Shift.objects.get(id=shift_id)
    if request.method == "POST":
        form = DropShiftRequestForm(shift, request.POST)
        if not form.is_valid():
            messages.error(request, f"Form Error: {form.errors}")
            return render(request, "change_or_drop_shift_req_response.html", {"success": False})
        data = form.cleaned_data
        DropRequest.objects.create(
            shift=shift,
            reason=data["reason"],
            state=State.NOT_VIEWED,
        )
        messages.success(request, "Shift Drop Successfully Requested.")
        response = render(request, "change_or_drop_shift_req_response.html", {"success": True, "shift_id": shift_id})
        description = f"""
            <b>Drop Request: {shift.kind}</b>
            <hr/>
            <b>Start:</b> {timezone.localtime(shift.start).strftime("%-I:%M %p")}<br/>
            <b>End:</b> {timezone.localtime(shift.start + shift.duration).strftime("%-I:%M %p")}<br/>
            <b>Location:</b> {shift.building.short_name}-{shift.room}
            <hr/>
            <b>Click on the shift to know more about the drop request</b>
        """
        response["HX-Trigger-After-Settle"] = json.dumps({
            "editShift": json.dumps({
                "id": f"{shift.id}",
                "start": shift.start.isoformat(),
                "end": (shift.start + shift.duration).isoformat(),
                "title": f"Drop Rquested: {shift.kind} - {shift.position}",
                "allDay": False,
                "color": color_coder(shift.kind),
                "textColor": "#FFA500",
                "extendedProps": {
                    "url": reverse("change_or_drop_shift_request", kwargs={"shift_id": shift.id}),
                    "description": description,
                }
            }),
        })
        return response
    if (shift.kind == ShiftKind.SI_SESSION or shift.kind == ShiftKind.CLASS) and shift.start - timezone.now() < timedelta(days=7):
        return render(request, "si_directions_7_days.html")
    form = DropShiftRequestForm(shift)
    return render(request, "just_form.html", {"form": form})