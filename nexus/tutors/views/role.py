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
    Course,
)

from users.models import (
    Positions,
    PositionChoices,
)

from ..models import (
    TutorRoleInfo,
)

from ..forms.role import (
    AssignRoleForm,
)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def assign_role(request):
    sem = Semester.objects.get_active_semester()
    tutor_positions = Positions.objects.filter(
        semester=sem, 
        position=PositionChoices.TUTOR
    )
    for position in tutor_positions:
        if not TutorRoleInfo.objects.filter(position=position).exists():
            TutorRoleInfo.objects.create(position=position)
    roles = TutorRoleInfo.objects.filter(position__semester=sem).all()
    context = {
        'roles': roles,
    }
    return render(request, 'tutor_assign_role.html', context)

@login_required
@restrict_to_http_methods("GET", "POST")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def update_role(request, role_id):
    if request.method == "POST":
        role = TutorRoleInfo.objects.get(id=role_id)
        POST = request.POST.copy()
        POST["position"] = role.position.id
        form = AssignRoleForm(role_id, POST, instance=role)
        if not form.is_valid():
            messages.error(request, f"Form Errors: {form.errors}")
            return render(request, "tutor_update_role_response.html", context={"success": False})
        data = form.cleaned_data
        role.assigned_courses.clear()
        for course in data["assigned_courses"]:
            role.assigned_courses.add(course)
        role.save()
        messages.success(request, "Role updated successfully.")
        context = {"success": True, "role": role}
        return render(request, "tutor_update_role_response.html", context=context)
    form = AssignRoleForm(role_id, instance=TutorRoleInfo.objects.get(id=role_id))
    response = render(request, 'just_form.html', {'form': form})
    response["HX-Trigger-After-Settle"] = json.dumps({"updateClicked": f"rt-{role_id}"})
    return response


class CourseAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Course.objects.all()
        if self.q:
            qs = qs.filter(Q(subject__short_name__icontains=self.q) | Q(number__icontains=self.q)).all()
        return qs