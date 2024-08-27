from datetime import timedelta

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.db.models import Q

from dal import autocomplete

from core.views import restrict_to_http_methods, restrict_to_groups

from users.models import (
    NexusUser,
    PositionGroups,
)

from ..models import (
    Shift,
    RecurringShift,
)

from ..forms.bulk_shift import (
    SelectGroup,
    BulkShiftAddForm,
)

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def group_shift(request):
    if request.method == "POST":
        form = SelectGroup(request.POST)
        if not form.is_valid():
            messages.error(request, f"Form Error: {form.errors}")
            return render(request, 'bulk_shift_response.html')
        group = form.cleaned_data['group']
        members = group.members.all()
        context = {
            'members': members,
            'group_id': group.id,
            'success': True,
        }
        return render(request, 'bulk_shift_response.html', context)
    form = SelectGroup()
    return render(request, 'bulk_shift.html', {'form': form})


@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def group_add_shift(request, group_id):
    if request.method == "POST":
        form = BulkShiftAddForm(group_id, request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form Error: {form.errors}")
            return render(request, 'group_add_shift_response.html')
        data = form.cleaned_data
        group = PositionGroups.objects.get(id=group_id)
        members = group.members.all()
        for member in members:
            Shift.objects.create(
                position=member,
                start=data['start'],
                duration=timedelta(hours=data['hours'], minutes=data['minutes']),
                building=data['building'],
                room=data['room'],
                kind=data['kind'],
                note=data['note'],
                document=data['document'],
                require_punch_in_out=data['require_punch_in_out'],
            )
        messages.success(request, f"Successfully added shifts to {group.name}")
        context = {
            'success': True,
            'group_id': group_id,
        }
        return render(request, 'group_add_shift_response.html', context)
    form = BulkShiftAddForm(group_id)
    return render(request, 'just_form.html', {'form': form})

class GroupAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = PositionGroups.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q).all()
        return qs