import json
from datetime import datetime, timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.db.models import Q

from dal import autocomplete

from core.views import restrict_to_http_methods, restrict_to_groups

from core.models import (
    Semester,
    Classes,
)

from users.models import (
    Positions,
    PositionChoices,
)

from ..models import (
    SIRoleInfo,
    SIShiftInfo,
)

from ..forms.role import (
    AssignRoleForm,
)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def assign_role(request):
    sem = Semester.objects.get_active_semester()
    si_positions = Positions.objects.filter(semester=sem, position=PositionChoices.SI)
    for position in si_positions:
        if not SIRoleInfo.objects.filter(position=position).exists():
            SIRoleInfo.objects.create(position=position)
    roles = SIRoleInfo.objects.filter(position__semester=sem).all()
    context = {
        'roles': roles,
    }
    return render(request, 'assign_role.html', context)

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def update_role(request, role_id):
    if request.method == "POST":
        role = SIRoleInfo.objects.get(id=role_id)
        POST = request.POST.copy()
        POST["position"] = role.position.id
        form = AssignRoleForm(role_id, POST)
        if not form.is_valid():
            messages.error(request, f"Form Errors: {form.errors}")
            return render(request, "update_role_response.html", context={"success": False})
        data = form.cleaned_data
        role.assigned_class = data["assigned_class"]
        role.save()
        messages.success(request, "Role updated successfully.")
        context = {"success": True, "role": role}
        return render(request, "update_role_response.html", context=context)
    form = AssignRoleForm(role_id)
    response = render(request, 'just_form.html', {'form': form})
    response["HX-Trigger-After-Settle"] = json.dumps({"updateClicked": f"rt-{role_id}"})
    return response


class ClassAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Classes.objects.all()
        if self.q:
            qs = qs.filter(Q(course__subject__short_name__icontains=self.q) | Q(course__number__icontains=self.q) | Q(faculty__first_name__icontains=self.q) | Q(faculty__last_name__icontains=self.q)).all()
        return qs
