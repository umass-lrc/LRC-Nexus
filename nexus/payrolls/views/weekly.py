from datetime import timedelta

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

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
    PayrollInHR,
    PayrollInHRViaLatePay,
    PayrollNotInHR,
    PayrollNotSigned,
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
        positions = data["position"]
    else:
        week = get_weekend(timezone.now().date())
        positions = [ps[0] for ps in PositionChoices.choices]
    
    # Optimize: Get all positions with select_related to avoid N+1 queries
    all_positions = Positions.objects.select_related('user', 'semester').filter(
        semester=Semester.objects.get_active_semester(),
        position__in=positions,
    )
    
    # Optimize: Get existing payrolls in a single query
    existing_payrolls = {
        p.position_id: p for p in Payroll.objects.select_related('position', 'position__user').filter(
            position__in=all_positions,
            week_end=week
        )
    }
    
    payrolls = []
    payrolls_to_create = []
    
    # Process positions efficiently
    for position in all_positions:
        if position.id in existing_payrolls:
            payroll = existing_payrolls[position.id]
        else:
            # Collect payrolls to create in bulk
            payroll = Payroll(
                position=position,
                week_end=week,
                status=PayrollStatus.NOT_IN_HR,
            )
            payrolls_to_create.append(payroll)
        
        payrolls.append(payroll)
    
    # Bulk create new payrolls
    if payrolls_to_create:
        created_payrolls = Payroll.objects.bulk_create(payrolls_to_create)
        # Re-fetch the created payrolls with their IDs to ensure they're properly loaded
        created_payroll_ids = [p.id for p in created_payrolls if p.id]
        if created_payroll_ids:
            created_payrolls_with_relations = list(Payroll.objects.select_related(
                'position', 'position__user'
            ).filter(id__in=created_payroll_ids))
            
            # Update the payrolls list with properly loaded objects
            created_index = 0
            for i, payroll in enumerate(payrolls):
                if not hasattr(payroll, 'id') or payroll.id is None:
                    if created_index < len(created_payrolls_with_relations):
                        payrolls[i] = created_payrolls_with_relations[created_index]
                        created_index += 1
    
    # Bulk create related payroll objects
    payroll_ids = [p.id for p in payrolls if hasattr(p, 'id') and p.id]
    if payroll_ids:
        # Get existing related objects to avoid duplicates
        existing_not_signed = set(PayrollNotSigned.objects.filter(payroll_id__in=payroll_ids).values_list('payroll_id', flat=True))
        existing_not_in_hr = set(PayrollNotInHR.objects.filter(payroll_id__in=payroll_ids).values_list('payroll_id', flat=True))
        existing_late_pay = set(PayrollInHRViaLatePay.objects.filter(payroll_id__in=payroll_ids).values_list('payroll_id', flat=True))
        existing_in_hr = set(PayrollInHR.objects.filter(payroll_id__in=payroll_ids).values_list('payroll_id', flat=True))
        
        # Bulk create missing related objects
        not_signed_to_create = [PayrollNotSigned(payroll_id=p.id) for p in payrolls if p.id not in existing_not_signed]
        not_in_hr_to_create = [PayrollNotInHR(payroll_id=p.id) for p in payrolls if p.id not in existing_not_in_hr]
        late_pay_to_create = [PayrollInHRViaLatePay(payroll_id=p.id) for p in payrolls if p.id not in existing_late_pay]
        in_hr_to_create = [PayrollInHR(payroll_id=p.id) for p in payrolls if p.id not in existing_in_hr]
        
        if not_signed_to_create:
            PayrollNotSigned.objects.bulk_create(not_signed_to_create, ignore_conflicts=True)
        if not_in_hr_to_create:
            PayrollNotInHR.objects.bulk_create(not_in_hr_to_create, ignore_conflicts=True)
        if late_pay_to_create:
            PayrollInHRViaLatePay.objects.bulk_create(late_pay_to_create, ignore_conflicts=True)
        if in_hr_to_create:
            PayrollInHR.objects.bulk_create(in_hr_to_create, ignore_conflicts=True)
    
    # Ensure all payrolls have IDs and are properly loaded
    final_payrolls = []
    for payroll in payrolls:
        if hasattr(payroll, 'id') and payroll.id:
            final_payrolls.append(payroll)
    
    # Add pagination to prevent loading too many payrolls at once
    paginator = Paginator(final_payrolls, 50)  # Show 50 payrolls per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, "weekly_all.html", {
        "payrolls": page_obj, 
        "week": week,
        "paginator": paginator,
        "page_obj": page_obj
    })

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Payroll Supervisor", "Staff Admin")
def single_weekly_payroll(request, payroll_id):
    # Optimize: Use select_related to avoid N+1 queries
    payroll = Payroll.objects.select_related(
        'position', 
        'position__user', 
        'position__semester',
        'in_hr',
        'not_in_hr',
        'late_pay',
        'not_signed'
    ).get(id=payroll_id)
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
    # Ensure related objects exist (create if missing)
    PayrollNotSigned.objects.get_or_create(payroll=payroll)
    PayrollNotInHR.objects.get_or_create(payroll=payroll)
    PayrollInHR.objects.get_or_create(payroll=payroll)
    PayrollInHRViaLatePay.objects.get_or_create(payroll=payroll)
    
    # Check conditions with proper error handling
    try:
        # Handle both timedelta and integer (microseconds) values
        total_hours = payroll.not_signed.total_hours
        has_unsigned_hours = False
        
        if isinstance(total_hours, int):
            has_unsigned_hours = total_hours > 0
        else:
            has_unsigned_hours = total_hours > timedelta(hours=0)
            
        if has_unsigned_hours:
            messages.error(request, f"User has not signed [few/all] of their shift for the week!")
    except AttributeError:
        pass  # Related object doesn't exist, skip check
    
    try:
        if not payroll.not_in_hr.approved_by_user:
            messages.warning(request, f"User has not approved the weekly payroll for this week!")
    except AttributeError:
        pass  # Related object doesn't exist, skip check
        
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