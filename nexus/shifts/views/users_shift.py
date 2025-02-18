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

from core.models import (
    Semester,
)

from users.models import (
    NexusUser,
)

from ..models import (
    Shift,
    RecurringShift,
)

from ..forms.users_shift import (
    UserLookUp,
    AddShiftForm,
    AddRecurringShiftForm,
)

from . import (
    get_color_coder_dict,
    color_coder,
)

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def users_shift(request):
    if request.method == "POST":
        form = UserLookUp(request.POST)
        if not form.is_valid():
            messages.error(request, f"Form Errors: {form.errors}")
            return render(request, "look_up_response.html")
        data = form.cleaned_data
        context = {
            "curr_user": data["user"],
            "success": True,
        }
        return render(request, "look_up_response.html", context)
    form = UserLookUp()
    context = {
        'form': form,
    }
    return render(request, "users_shift.html", context)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def user_calendar(request, user_id):
    response = render(request, "color_coder.html", {'colors': get_color_coder_dict()})
    response["HX-Trigger-After-Settle"] = json.dumps({"userCalendar": user_id})
    return response

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def get_user_shifts(request):
    user = NexusUser.objects.get(id=request.GET["user_id"])
    start = datetime.fromisoformat(request.GET["start"])
    end = datetime.fromisoformat(request.GET["end"])
    
    shifts = Shift.objects.filter(position__user=user, start__gte=start, start__lte=end).all()
    shifts_data = []
    for shift in shifts:
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
        shifts_data.append({
            "id": str(shift.id),
            "start": shift.start.isoformat(),
            "end": (shift.start + shift.duration).isoformat(),
            "title": str(shift),
            "allDay": False,
            "color": color_coder(shift.kind),
            "extendedProps": {
                "url": reverse("edit_or_drop_shift", kwargs={"shift_id": shift.id}),
                "description": description,
            }
        })
    return JsonResponse(shifts_data, safe=False)

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def add_shift(request, user_id):
    if request.method == "POST":
        form = AddShiftForm(user_id, False, request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form Errors: {form.errors}")
            return render(request, "add_shift_response.html")
        data = form.cleaned_data
        shift = Shift.objects.create(
            position=data["position"],
            start=data["start"],
            duration=timedelta(hours=data["hours"], minutes=data["minutes"]),
            building=data["building"],
            room=data["room"],
            kind=data["kind"],
            note=data["note"],
            document=data["document"],
            require_punch_in_out=data["require_punch_in_out"],
        )
        messages.success(request, "Shift created successfully.")
        context = {
            "success": True,
            "user_id": user_id,
        }
        response = render(request, "add_shift_response.html", context)
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
        response["HX-Trigger-After-Settle"] = json.dumps({
            "addEvent": json.dumps({
                "id": str(shift.id),
                "start": shift.start.isoformat(),
                "end": (shift.start + shift.duration).isoformat(),
                "title": str(shift),
                "allDay": False,
                "color": color_coder(shift.kind),
                "extendedProps": {
                    "url": reverse("edit_or_drop_shift", kwargs={"shift_id": shift.id}),
                    "description": description,
                }
            })
        })
        return response
    form = AddShiftForm(user_id, False)
    return render(request, "just_form.html", {'form': form})

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def edit_or_drop_shift(request, shift_id):
    context = {
        "shift_id": shift_id,
    }
    return render(request, "edit_or_drop.html", context)

@login_required
@restrict_to_http_methods("DELETE")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def drop_shift(request, shift_id):
    shift = Shift.objects.get(id=shift_id)
    if shift.attendance_info.attended:
        messages.error(request, "Shift has already been signed. Cannot delete.")
        context = { "success": False, "shift_id": shift_id }
        return render(request, "delete_shift.html", context)
    shift.delete()
    messages.success(request, "Shift deleted successfully.")
    context = {
        "success": True,
        "shift_id": shift_id,
    }
    response = render(request, "delete_shift.html", context)
    response["HX-Trigger-After-Settle"] = json.dumps({
        "dropEvent": str(shift.id),
    })
    return response

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def edit_shift(request, shift_id):
    shift = Shift.objects.get(id=shift_id)
    if request.method == "POST":
        form = AddShiftForm(shift.position.user.id, True, request.POST, request.FILES, instance=shift)
        if not form.is_valid():
            messages.error(request, f"Form Errors: {form.errors}")
            return render(request, "edit_shift_response.html")
        data = form.cleaned_data
        shift.position = data["position"]
        shift.start = data["start"]
        shift.duration = timedelta(hours=data["hours"], minutes=data["minutes"])
        shift.building = data["building"]
        shift.room = data["room"]
        shift.kind = data["kind"]
        shift.note = data["note"]
        shift.document = data["document"]
        shift.recurring_shift = None
        shift.require_punch_in_out = data["require_punch_in_out"]
        shift.save()
        messages.success(request, "Shift updated successfully.")
        context = {
            "success": True,
            "shift_id": shift.id,
        }
        response = render(request, "edit_shift_response.html", context)
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
        response["HX-Trigger-After-Settle"] = json.dumps({
            "editEvent": json.dumps({
                "id": str(shift.id),
                "start": shift.start.isoformat(),
                "end": (shift.start + shift.duration).isoformat(),
                "title": str(shift),
                "allDay": False,
                "color": color_coder(shift.kind),
                "extendedProps": {
                    "url": reverse("edit_or_drop_shift", kwargs={"shift_id": shift.id}),
                    "description": description,
                }
            })
        })
        return response
    form = AddShiftForm(shift.position.user.id, True, instance=shift)
    form.fields["hours"].initial = shift.duration.seconds // 3600
    form.fields["minutes"].initial = (shift.duration.seconds % 3600) // 60
    context = { "form": form}
    return render(request, "edit_shift_initial.html", context)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def add_edit_recurring(request, user_id):
    user = NexusUser.objects.get(id=user_id)
    recurring_shifts = RecurringShift.objects.filter(position__user=user).all()
    current_datetime = timezone.now().date()
    current_recurring_shifts = recurring_shifts.filter(start_date__lte=current_datetime, end_date__gte=current_datetime)
    inactive_recurring_shifts = recurring_shifts.exclude(start_date__lte=current_datetime, end_date__gte=current_datetime)
    context = {
        "user_id": user_id,
        "current_recurring_shifts": current_recurring_shifts,
        "inactive_recurring_shifts": inactive_recurring_shifts,
        "edit_form": AddRecurringShiftForm(user_id, True, blank=True),
    }
    return render(request, "add_edit_recurring.html", context)

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def add_recurring(request, user_id):
    if request.method == "POST":
        form = AddRecurringShiftForm(user_id, False, request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form Errors: {form.errors}")
            context = { "success": False }
            return render(request, "add_recurring_response.html", context)
        data = form.cleaned_data
        rshift = RecurringShift.objects.create(
            position=data["position"],
            day=data["day"],
            start_time=data["start_time"],
            duration=timedelta(hours=data["hours"], minutes=data["minutes"]),
            building=data["building"],
            room=data["room"],
            kind=data["kind"],
            note=data["note"],
            document=data["document"],
            require_punch_in_out=data["require_punch_in_out"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
        messages.success(request, "Recurring Shift created successfully.")
        context = {
            "success": True,
            "user_id": user_id,
            "rshift": rshift,
        }
        shifts_events = []
        shifts = Shift.objects.filter(recurring_shift=rshift).all()
        for shift in shifts:
            shifts_events.append(json.dumps({
                "id": str(shift.id),
                "start": shift.start.isoformat(),
                "end": (shift.start + shift.duration).isoformat(),
                "title": str(shift),
                "allDay": False,
                "color": color_coder(shift.kind),
                "extendedProps": {
                    "url": reverse("edit_shift", kwargs={"shift_id": shift.id}),
                }
            }))
        response = render(request, "add_recurring_response.html", context)
        response["HX-Trigger-After-Settle"] = json.dumps({
            "addRecurring": json.dumps(shifts_events),
        })
        return response
    form = AddRecurringShiftForm(user_id, False)
    return render(request, "just_form.html", {'form': form})

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def edit_recurring(request, rshift_id):
    rshift = RecurringShift.objects.get(id=rshift_id)
    if request.method == "POST":
        form = AddRecurringShiftForm(rshift.position.user.id, True, request.POST, request.FILES, instance=rshift)
        if not form.is_valid():
            messages.error(request, f"Form Errors: {form.errors}")
            return render(request, "edit_recurring_response.html")
        data = form.cleaned_data
        rshift.position = data["position"]
        rshift.day = data["day"]
        rshift.start_time = data["start_time"]
        rshift.duration = timedelta(hours=data["hours"], minutes=data["minutes"])
        rshift.building = data["building"]
        rshift.room = data["room"]
        rshift.kind = data["kind"]
        rshift.note = data["note"]
        rshift.document = data["document"]
        rshift.require_punch_in_out = data["require_punch_in_out"]
        rshift.start_date = data["start_date"]
        rshift.end_date = data["end_date"]
        rshift.save()
        messages.success(request, "Recurring Shift updated successfully.")
        context = {
            "rshift": rshift,
            "success": True,
        }
        response = render(request, "edit_recurring_response.html", context)
        shifts_events = []
        shifts = Shift.objects.filter(recurring_shift=rshift).all()
        for shift in shifts:
            shifts_events.append(json.dumps({
                "id": str(shift.id),
                "start": shift.start.isoformat(),
                "end": (shift.start + shift.duration).isoformat(),
                "title": str(shift),
                "allDay": False,
                "color": color_coder(shift.kind),
                "extendedProps": {
                    "url": reverse("edit_shift", kwargs={"shift_id": shift.id}),
                }
            }))
        response["HX-Trigger-After-Settle"] = json.dumps({
            "changeRecurring": json.dumps(shifts_events),
        })
        return response
    form = AddRecurringShiftForm(rshift.position.user.id, True, instance=rshift)
    form.fields["hours"].initial = rshift.duration.seconds // 3600
    form.fields["minutes"].initial = (rshift.duration.seconds % 3600) // 60
    response = render(request, "just_form.html", {'form': form})
    response["HX-Trigger-After-Settle"] = json.dumps({"recurringUpdateClicked": f"rt-{rshift.id}"})
    return response

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def record_meeting(request, user_id):
    if request.method == "POST":
        return render(request, "work_in_progress.html")
    return render(request, "work_in_progress.html")

class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = NexusUser.objects.all()
        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q)).all()
        return qs