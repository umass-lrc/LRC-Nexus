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
    Buildings,
)

from shifts.models import (
    AttendanceInfo,
    Shift,
    ShiftKind,
    get_weekend,
)

from payrolls.models import (
    Payroll,
    PayrollInHR,
    PayrollInHRViaLatePay,
    PayrollNotInHR,
    PayrollStatus,
)

from ..forms.payroll import (
    PunchInForm,
    PunchOutForm,
    SignShiftForm,
    ShiftPunchInForm,
    ShiftPunchOutForm,
)

@login_required
@restrict_to_http_methods('GET')
def get_user_payroll_page(request):
    user = request.user
    active_sem = Semester.objects.get_active_semester()
    positions_punch_in_out = Positions.objects.filter(Q(user=user) & Q(semester=active_sem) & ~Q(position__in=[PositionChoices.SI, PositionChoices.GROUP_TUTOR])).all()
    # att_not_signed = AttendanceInfo.objects.filter(shift__position__user=user, shift__start__lte=timezone.now(), signed=False).values_list('shift__id', flat=True)
    not_signed_shifts = Shift.objects.filter(position__user=user, start__lte=timezone.now(), attendance_info__signed=False).all()
    punch_in_out_shifts = Shift.objects.filter(
        (Q(position__user=user) & Q(require_punch_in_out=True)) & 
        (
            (Q(attendance_info__punch_in_time__isnull=False) & Q(attendance_info__punch_out_time__isnull=True)) | 
            (Q(start__gte=(timezone.now() - timedelta(hours=8))) & Q(start__lte=(timezone.now() + timedelta(minutes=30))) & Q(attendance_info__punch_in_time__isnull=True))
        )
    ).all()
    shifts_punch_in_but_not_out = Shift.objects.filter(position__user=user, attendance_info__punch_in_time__isnull=False, attendance_info__punch_out_time__isnull=True).all()
    not_signed_shifts_ = []
    for shift in not_signed_shifts:
        if shift in shifts_punch_in_but_not_out:
            continue
        not_signed_shifts_.append(shift)
    context = {
        'positions_punch_in_out': positions_punch_in_out,
        'not_signed_shifts': not_signed_shifts_,
        'punch_in_out_shifts': punch_in_out_shifts,
    }
    return render(request, 'user_payroll_main.html', context)

@login_required
@restrict_to_http_methods('GET','POST')
def punch_in_out_position(request, position_id):
    user = request.user
    position = Positions.objects.get(id=position_id)
    att_info = AttendanceInfo.objects.filter(shift__position=position, shift__require_punch_in_out=False, punch_in_time__isnull=False, punch_out_time__isnull=True, attended=False)
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
            att_info.save()
            messages.success(request, 'Punched in successfully.')
        else:
            punch_out_time = timezone.now()
            duration = punch_out_time - att_info.shift.start
            att_info.shift.duration = duration
            att_info.shift.save()
            att_info.punch_out_time = punch_out_time.time()
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
@restrict_to_http_methods('GET','POST')
def shift_punch_in_out(request, shift_id):
    user = request.user
    shift = Shift.objects.get(id=shift_id)
    att_info = AttendanceInfo.objects.filter(shift=shift, punch_in_time__isnull=False, punch_out_time__isnull=True)
    punched_in = att_info.exists()
    if punched_in:
        att_info = att_info.first()
    
    if request.method == 'POST':
        form = None
        if not punched_in:
            form = ShiftPunchInForm(shift, request.POST)
        else:
            form = ShiftPunchOutForm(shift, request.POST)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'shift_punch_in_out_response.html', context={'success': False})
        data = form.cleaned_data
        if not punched_in:
            punch_in_time = timezone.now()
            att_info = AttendanceInfo.objects.get(shift=shift)
            att_info.punch_in_time = punch_in_time.time()
            att_info.save()
            messages.success(request, 'Punched in successfully.')
        else:
            punch_out_time = timezone.now()
            start = punch_out_time.replace(hour=att_info.punch_in_time.hour, minute=att_info.punch_in_time.minute, second=att_info.punch_in_time.second)
            if punch_out_time < start:
                start = start - timedelta(days=1)
            att_info.shift.start = start
            att_info.shift.duration = punch_out_time - start
            att_info.shift.save()
            att_info.punch_out_time = punch_out_time.time()
            att_info.save()
            messages.success(request, 'Punched out successfully.')
        context = {
            'shift': shift,
            'success': True,
            'punched_out': punched_in,
        }
        return render(request, 'shift_punch_in_out_response.html', context)
    form = ShiftPunchInForm(shift) if not punched_in else ShiftPunchOutForm(shift)
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
            
            if shift.kind == ShiftKind.SI_SESSION or shift.kind == ShiftKind.GROUP_TUTORING:
                duration = timedelta(hours=2)
                if shift.duration > timedelta(hours=1, minutes=15):
                    duration += (shift.duration-timedelta(hours=1, minutes=15))*(timedelta(hours=1)/timedelta(minutes=45))
                if duration > timedelta(hours=3):
                    duration = timedelta(hours=3)
                prep_shift = Shift.objects.create(
                    position=shift.position,
                    start=shift.start,
                    duration=duration,
                    building=Buildings.objects.get(short_name='ZOOM'),
                    room="Home",
                    kind=ShiftKind.PREPARATION,
                )
                prep_shift.attendance_info.attended = True
                prep_shift.attendance_info.signed = True
                prep_shift.attendance_info.sign_datetime = timezone.now()
                prep_shift.attendance_info.save()
                prep_shift.attendance_info.did_attend()
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

@login_required
@restrict_to_http_methods('GET')
def get_user_payslips(request):
    user = request.user
    active_sem = Semester.objects.get_active_semester()
    positions = Positions.objects.filter(user=user, semester=active_sem).all()
    week_ends = Payroll.objects.filter(position__in=positions, week_end__lte=get_weekend(timezone.now().date())).all().order_by('-week_end').values_list('week_end', flat=True).distinct()
    context = {
        'week_ends': week_ends,
    }
    return render(request, 'user_payslips.html', context)

@login_required
@restrict_to_http_methods('GET')
def get_payslip_for(request, week_end):
    user = request.user
    active_sem = Semester.objects.get_active_semester()
    positions = Positions.objects.filter(user=user, semester=active_sem).all()
    payrolls = Payroll.objects.filter(position__in=positions, week_end=week_end).all()
    for position in positions:
        if not payrolls.filter(position=position, week_end=week_end).exists():
            Payroll.objects.create(
                position=position,
                week_end=week_end,
                status=PayrollStatus.NOT_IN_HR,
            )
    context = {
        'payrolls': payrolls,
        'payroll_rows': len(payrolls)*5,
        'week_end': week_end,
    }
    return render(request, 'payslip.html', context)