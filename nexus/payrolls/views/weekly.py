from datetime import timedelta

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
    Positions,
    PositionChoices,
)

from shifts.models import (
    get_weekend,
)

from ..forms.weekly import (
    WeekSelectForm,
    StatusForm,
)

from ..models import (
    Payroll,
    PayrollStatus,
)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Payroll Supervisor", "Staff Admin")
def weekly_payroll(request):
    form = WeekSelectForm(initial={"week": timezone.now().date()})
    context = {
        "form": form,
        "this_week": get_weekend(timezone.now().date()),
    }
    return render(request, "weekly_main.html", context)

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Payroll Supervisor", "Staff Admin")
def all_weekly_payroll(request):
    week, positions = None, None
    if request.method == "POST":
        form = WeekSelectForm(request.POST)
        if not form.is_valid():
            messages.error(request, f"Form Error: {form.errors}")
            return render(request, "weekly_response.html", {"form": form})
        data = form.cleaned_data
        week = get_weekend(data["week"])
        print(data['week'], week)
        positions = data["position"]
    else:
        week = get_weekend(timezone.now().date())
        positions = [ps[0] for ps in PositionChoices.choices]
    all_positions = Positions.objects.filter(
        semester=Semester.objects.get_active_semester(),
        position__in=positions,
    )
    payrolls = []
    for position in all_positions:
        payroll = Payroll.objects.filter(position=position, week_end=week)
        if not payroll:
            payroll = Payroll.objects.create(
                position=position,
                week_end=week,
                status=PayrollStatus.NOT_IN_HR,
            )
        else:
            payroll = payroll[0]
        payrolls.append(payroll)
    
    return render(request, "weekly_all.html", {"payrolls": payrolls, "week": week})

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Payroll Supervisor", "Staff Admin")
def single_weekly_payroll(request, payroll_id):
    payroll = Payroll.objects.get(id=payroll_id)
    if request.method == "POST":
        form = StatusForm(request.POST, instance=payroll)
        if not form.is_valid():
            messages.error(request, f"Form Error: {form.errors}")
        else:
            data = form.cleaned_data
            status = data["status"]
            if payroll.status == PayrollStatus.IN_HR_ON_TIME:
                nih = payroll.not_in_hr
                ih = payroll.in_hr
                ih.sunday_hours += nih.sunday_hours
                nih.sunday_hours = timedelta(hours=0)
                ih.monday_hours += nih.monday_hours
                nih.monday_hours = timedelta(hours=0)
                ih.tuesday_hours += nih.tuesday_hours
                nih.tuesday_hours = timedelta(hours=0)
                ih.wednesday_hours += nih.wednesday_hours
                nih.wednesday_hours = timedelta(hours=0)
                ih.thursday_hours += nih.thursday_hours
                nih.thursday_hours = timedelta(hours=0)
                ih.friday_hours += nih.friday_hours
                nih.friday_hours = timedelta(hours=0)
                ih.saturday_hours += nih.saturday_hours
                nih.saturday_hours = timedelta(hours=0)
                ih.total_hours += nih.total_hours
                nih.total_hours = timedelta(hours=0)
                nih.save()
                ih.save()
                payroll.status = status
                payroll.save()
                messages.success(request, f"Payroll Status Updated!")
            elif payroll.status == PayrollStatus.IN_HR_VIA_LATE_PAY:
                nih = payroll.not_in_hr
                lp = payroll.late_pay
                lp.sunday_hours += nih.sunday_hours
                nih.sunday_hours = timedelta(hours=0)
                lp.monday_hours += nih.monday_hours
                nih.monday_hours = timedelta(hours=0)
                lp.tuesday_hours += nih.tuesday_hours
                nih.tuesday_hours = timedelta(hours=0)
                lp.wednesday_hours += nih.wednesday_hours
                nih.wednesday_hours = timedelta(hours=0)
                lp.thursday_hours += nih.thursday_hours
                nih.thursday_hours = timedelta(hours=0)
                lp.friday_hours += nih.friday_hours
                nih.friday_hours = timedelta(hours=0)
                lp.saturday_hours += nih.saturday_hours
                nih.saturday_hours = timedelta(hours=0)
                lp.total_hours += nih.total_hours
                nih.total_hours = timedelta(hours=0)
                nih.save()
                lp.save()
                payroll.status = status
                payroll.save()
                messages.success(request, f"Payroll Status Updated!")
            if payroll.status == PayrollStatus.NOT_IN_HR:
                payroll = Payroll.objects.get(id=payroll_id)
                messages.error(request, f"Payroll Status Not Updated! Can't update status to Not In HR!")
    if payroll.not_signed.total_hours > timedelta(hours=0):
        messages.warning(request, f"User has not signed [few/all] of their payroll for the week!")
    form = StatusForm(instance=payroll)
    color = "tbody-red" if payroll.status == PayrollStatus.NOT_IN_HR else "tbody-green" if payroll.status == PayrollStatus.IN_HR_ON_TIME else "tbody-yellow"
    context = {
        'color': color,
        'id': payroll.id,
        'form': form,
        'last_name': payroll.position.user.last_name,
        'first_name': payroll.position.user.first_name,
        'position': payroll.position.get_position_display(),
        'in_hr': {
            'sun_hours': payroll.in_hr.sunday_hours,
            'mon_hours': payroll.in_hr.monday_hours,
            'tue_hours': payroll.in_hr.tuesday_hours,
            'wed_hours': payroll.in_hr.wednesday_hours,
            'thu_hours': payroll.in_hr.thursday_hours,
            'fri_hours': payroll.in_hr.friday_hours,
            'sat_hours': payroll.in_hr.saturday_hours,
            'total_hours': payroll.in_hr.total_hours,
        },
        'not_in_hr': {
            'sun_hours': payroll.not_in_hr.sunday_hours,
            'mon_hours': payroll.not_in_hr.monday_hours,
            'tue_hours': payroll.not_in_hr.tuesday_hours,
            'wed_hours': payroll.not_in_hr.wednesday_hours,
            'thu_hours': payroll.not_in_hr.thursday_hours,
            'fri_hours': payroll.not_in_hr.friday_hours,
            'sat_hours': payroll.not_in_hr.saturday_hours,
            'total_hours': payroll.not_in_hr.total_hours,
        },
        'late_pay': {
            'sun_hours': payroll.late_pay.sunday_hours,
            'mon_hours': payroll.late_pay.monday_hours,
            'tue_hours': payroll.late_pay.tuesday_hours,
            'wed_hours': payroll.late_pay.wednesday_hours,
            'thu_hours': payroll.late_pay.thursday_hours,
            'fri_hours': payroll.late_pay.friday_hours,
            'sat_hours': payroll.late_pay.saturday_hours,
            'total_hours': payroll.late_pay.total_hours,   
        },
        'total': {
            'sun_hours': payroll.in_hr.sunday_hours + payroll.not_in_hr.sunday_hours + payroll.late_pay.sunday_hours,
            'mon_hours': payroll.in_hr.monday_hours + payroll.not_in_hr.monday_hours + payroll.late_pay.monday_hours,
            'tue_hours': payroll.in_hr.tuesday_hours + payroll.not_in_hr.tuesday_hours + payroll.late_pay.tuesday_hours,
            'wed_hours': payroll.in_hr.wednesday_hours + payroll.not_in_hr.wednesday_hours + payroll.late_pay.wednesday_hours,
            'thu_hours': payroll.in_hr.thursday_hours + payroll.not_in_hr.thursday_hours + payroll.late_pay.thursday_hours,
            'fri_hours': payroll.in_hr.friday_hours + payroll.not_in_hr.friday_hours + payroll.late_pay.friday_hours,
            'sat_hours': payroll.in_hr.saturday_hours + payroll.not_in_hr.saturday_hours + payroll.late_pay.saturday_hours,
            'total_hours': payroll.in_hr.total_hours + payroll.not_in_hr.total_hours + payroll.late_pay.total_hours,
        },
    }
    return render(request, "weekly_single.html", context)