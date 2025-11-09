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
from ..forms.payroll import shift_type_choices

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
            "title": str(shift),
            "allDay": False,
            "color": color_coder(shift.kind),
            "extendedProps": {
                "url": reverse("change_or_drop_shift_request", kwargs={"shift_id": shift.id}),
                "shift_id": shift.id,
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
            "title": f"Drop Rquested: {shift.kind} - {shift.position}",
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
    shift = Shift.objects.filter(id=shift_id, dropped=False).first()
    if shift is None:
        return render(request, "change_or_drop_shift_req_response.html", {"success": False})
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
    # Render manual HTML form to work around Crispy hanging with PostgreSQL
    
    # Workaround: Render form fields manually to avoid Crispy hanging with PostgreSQL
    from django.http import HttpResponse
    from core.models import Buildings
    
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    
    buildings = Buildings.objects.all()
    
    # Format start datetime for datetime-local input (YYYY-MM-DDTHH:MM)
    start_datetime = timezone.localtime(shift.start).strftime('%Y-%m-%dT%H:%M')
    
    # Calculate hours and minutes from duration
    total_seconds = int(shift.duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    html = f'''
    <form method="post" hx-post="/students/calendar/change-shift-request/{shift.id}/" hx-swap="multi:#shift-request-message:innerHTML,#shift-request:innerHTML">
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
        <div class="mb-3 form-floating">
            <input type="text" value="{shift}" class="form-control" disabled>
            <label>Current Shift</label>
            <input type="hidden" name="shift" value="{shift.id}">
        </div>
        
        <div class="mb-3 form-floating">
            <input type="datetime-local" name="start" class="form-control" id="id_start" value="{start_datetime}" required>
            <label for="id_start">Start Date/Time</label>
        </div>
        
        <label class="form-label requiredField">Duration<span class="asteriskField">*</span></label>
        <div class="row mb-3">
            <div class="col-md-6">
                <div class="form-floating">
                    <input type="number" name="hours" min="0" max="24" class="form-control" value="{hours}" required>
                    <label>Hours</label>
                </div>
            </div>
            <div class="col-md-6">
                <div class="form-floating">
                    <input type="number" name="minutes" min="0" max="59" class="form-control" value="{minutes}" required>
                    <label>Minutes</label>
                </div>
            </div>
        </div>
        
        <div class="mb-3 form-floating">
            <select name="building" class="form-select" id="id_building" required>
    '''
    
    for building in buildings:
        selected = 'selected' if building.short_name == shift.building.short_name else ''
        html += f'<option value="{building.short_name}" {selected}>{building.name}</option>'
    
    html += f'''
            </select>
            <label for="id_building">Building</label>
        </div>
        
        <div class="mb-3 form-floating">
            <input type="text" name="room" class="form-control" id="id_room" value="{shift.room}" maxlength="10" required>
            <label for="id_room">Room</label>
        </div>
        
        <div class="mb-3 form-floating">
            <select name="kind" class="form-select" id="id_kind" required>
    '''
    
    # Get allowed kinds for this position type
    position_type = shift.position.position
    allowed_kinds = shift_type_choices.get(position_type, [])
    
    # If position type is in mapping, only show allowed kinds
    # Otherwise, fall back to all kinds
    if allowed_kinds:
        for kind in allowed_kinds:
            selected = 'selected' if kind.value == shift.kind else ''
            html += f'<option value="{kind.value}" {selected}>{kind.label}</option>'
    else:
        # Fallback to all kinds if position type not in mapping
        for kind_value, kind_label in ShiftKind.choices:
            selected = 'selected' if kind_value == shift.kind else ''
            html += f'<option value="{kind_value}" {selected}>{kind_label}</option>'
    
    html += '''
            </select>
            <label for="id_kind">Kind</label>
        </div>
        
        <div class="mb-3 form-floating">
            <textarea name="reason" class="form-control" id="id_reason" required style="height: 100px;"></textarea>
            <label for="id_reason">Reason</label>
        </div>
        
        <div class="text-center">
            <button type="submit" class="btn btn-primary">Make Change Request</button>
        </div>
    </form>
    '''
    
    return HttpResponse(html)

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
    
    # Render manual HTML form to work around Crispy hanging with PostgreSQL
    from django.http import HttpResponse
    from django.middleware.csrf import get_token
    
    csrf_token = get_token(request)
    html = f'''
    <form method="post" hx-post="/students/calendar/drop-shift-request/{shift.id}/" hx-swap="multi:#shift-request-message:innerHTML,#shift-request:innerHTML">
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
        
        <div class="mb-3 form-floating">
            <input type="text" value="{shift}" class="form-control" disabled>
            <label>Current Shift</label>
            <input type="hidden" name="shift" value="{shift.id}">
        </div>
        
        <div class="mb-3 form-floating">
            <select class="form-select" id="id_kind" disabled>
    '''
    
    # Get allowed kinds for this position type (for display purposes)
    position_type = shift.position.position
    allowed_kinds = shift_type_choices.get(position_type, [])
    
    # If position type is in mapping, only show allowed kinds
    # Otherwise, fall back to all kinds
    if allowed_kinds:
        for kind in allowed_kinds:
            selected = 'selected' if kind.value == shift.kind else ''
            html += f'<option value="{kind.value}" {selected}>{kind.label}</option>'
    else:
        # Fallback to all kinds if position type not in mapping
        for kind_value, kind_label in ShiftKind.choices:
            selected = 'selected' if kind_value == shift.kind else ''
            html += f'<option value="{kind_value}" {selected}>{kind_label}</option>'
    
    html += '''
            </select>
            <label for="id_kind">Kind</label>
        </div>
        
        <div class="mb-3 form-floating">
            <textarea name="reason" class="form-control" id="id_reason" required style="height: 150px;"></textarea>
            <label for="id_reason">Reason for Dropping</label>
        </div>
        
        <p class="text-center">
            <b>Are you sure you want to drop this shift?</b>
        </p>
        
        <div class="text-center">
            <button type="submit" class="btn btn-danger">Make Drop Request</button>
        </div>
    </form>
    '''
    
    return HttpResponse(html)