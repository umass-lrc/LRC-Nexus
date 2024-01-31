from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render, redirect
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
)

from ..forms.payroll import (
    PunchInForm,
    PunchOutForm,
    SignShiftForm,
)

@login_required
@restrict_to_http_methods('GET')
def get_user_payroll_page(request):
    user = request.user
    active_sem = Semester.objects.get_active_semester()
    positions_punch_in_out = Positions.objects.filter(Q(user=user) & Q(semester=active_sem) & ~Q(position__in=[PositionChoices.SI, PositionChoices.GROUP_TUTOR])).all()
    att_not_signed = AttendanceInfo.objects.filter(shift__position__user=user, signed=False).values_list('shift__id', flat=True)
    not_signed_shifts = Shift.objects.filter(id__in=att_not_signed).all()
    context = {
        'positions_punch_in_out': positions_punch_in_out,
        'not_signed_shifts': not_signed_shifts,
    }
    return render(request, 'user_payroll_main.html', context)

@login_required
@restrict_to_http_methods('GET','POST')
def punch_in_out_position(request, position_id):
    user = request.user
    position = Positions.objects.get(id=position_id)
    att_info = AttendanceInfo.objects.filter(shift__position=position, punch_in_time__isnull=False, punch_out_time__isnull=True)
    punched_in = att_info.exists()
    if punched_in:
        att_info = att_info.first()
    
    if request.method == 'POST':
        form = None
        if not punched_in:
            form = PunchInForm(position, request.POST)
        else:
            form = PunchOutForm(position, request.POST, initial={'building': att_info.shift.building, 'room': att_info.shift.room, 'kind': att_info.shift.kind})
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'punch_in_out_response.html', context={'success': False})
        data = form.cleaned_data
        if not punched_in:
            punch_in_time = timezone.now()
            shift = Shift.objects.create(
                position=position,
                start=punch_in_time,
                duration=timedelta(hours=0),
                building=data['building'],
                room=data['room'],
                kind=data['kind'],
            )
            att_info = AttendanceInfo.objects.get(shift=shift)
            att_info.punch_in_time = punch_in_time.time()
            att_info.attended = True
            att_info.save()
            att_info.did_attend()
            messages.success(request, 'Punched in successfully.')
        else:
            punch_out_time = timezone.now()
            duration = punch_out_time - att_info.shift.start
            att_info.shift.duration = duration
            att_info.shift.save()
            att_info.punch_out_time = punch_out_time.time()
            att_info.signed = True
            att_info.sign_datetime = punch_out_time
            att_info.save()
            messages.success(request, 'Punched out successfully.')
        context = {
            'position': position,
            'success': True,
        }
        return render(request, 'punch_in_out_response.html', context)
    form = PunchInForm(position) if not punched_in else PunchOutForm(position, initial={'building': att_info.shift.building, 'room': att_info.shift.room, 'kind': att_info.shift.kind})
    context = {
        'form': form,
    }
    return render(request, 'just_form.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
def sign_shift(request, shift_id):
    shift = Shift.objects.get(id=shift_id)
    if request.method == "POST":
        form = SignShiftForm(request.POST, initial={
            'position': shift.position,
            'start': shift.start,
            'duration': shift.duration,
            'building': shift.building, 
            'room': shift.room, 
            'kind': shift.kind,
            'shift_id': shift.id,
            'shift': shift,
        })
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'sign_shift_response.html', context={'success': False})
        data = form.cleaned_data
        if 'did_attend' in request.POST:
            att = AttendanceInfo.objects.get(shift=shift)
            att.attended = True
            att.signed = True
            att.sign_datetime = timezone.now()
            att.save()
            att.did_attend()
        elif 'did_not_attend' in request.POST:
            att = AttendanceInfo.objects.get(shift=shift)
            att.attended = False
            att.signed = True
            att.sign_datetime = timezone.now()
            att.save()
            att.did_not_attend()
        messages.success(request, 'Shift signed successfully.')
        return render(request, 'sign_shift_response.html', context={'success': True, 'shift_id': shift.id})
    form = SignShiftForm(initial={
        'position': shift.position,
        'start': shift.start,
        'duration': shift.duration,
        'building': shift.building, 
        'room': shift.room, 
        'kind': shift.kind,
        'shift_id': shift.id,
        'shift': shift,
    })
    return render(request, 'just_form.html', context={'form': form})