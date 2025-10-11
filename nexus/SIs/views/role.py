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
)

from ..forms.role import (
    AssignRoleForm,
)

@login_required
@restrict_to_http_methods("GET")
@restrict_to_groups("Staff Admin", "SI Supervisor", "Tutor Supervisor", "OURS Supervisor", "Payroll Supervisor")
def assign_role(request):
    sem = Semester.objects.get_active_semester()
    
    # Optimize: Get SI positions with select_related
    si_positions = Positions.objects.select_related('user').filter(
        semester=sem, 
        position=PositionChoices.SI
    )
    
    # Optimize: Get existing roles in bulk to avoid N+1 queries
    existing_role_positions = set(
        SIRoleInfo.objects.filter(
            position__semester=sem
        ).values_list('position_id', flat=True)
    )
    
    # Bulk create missing roles
    roles_to_create = []
    for position in si_positions:
        if position.id not in existing_role_positions:
            roles_to_create.append(SIRoleInfo(position=position))
    
    if roles_to_create:
        SIRoleInfo.objects.bulk_create(roles_to_create, ignore_conflicts=True)
    
    # Optimize: Get roles with select_related (no pagination needed)
    roles = SIRoleInfo.objects.select_related(
        'position', 'position__user', 'assigned_class', 'assigned_class__course', 'assigned_class__course__subject', 'assigned_class__faculty'
    ).filter(position__semester=sem).order_by('position__user__last_name', 'position__user__first_name')
    
    # Pre-compute class strings efficiently to avoid expensive __str__ calls
    roles_with_classes = []
    for role in roles:
        # Pre-compute the class display string without calling expensive __str__ method
        if role.assigned_class:
            # Build a simple class string without expensive database queries
            class_str = f"{role.assigned_class.course} - {role.assigned_class.faculty}"
        else:
            class_str = "No class assigned"
            
        roles_with_classes.append({
            'role': role,
            'class_string': class_str,
            'has_class': role.assigned_class is not None
        })
    
    context = {
        'roles_with_classes': roles_with_classes,
        'roles': roles,  # Keep for compatibility
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
        form = AssignRoleForm(role_id, POST, instance=role)
        if not form.is_valid():
            messages.error(request, f"Form Errors: {form.errors}")
            return render(request, "update_role_response.html", context={"success": False})
        data = form.cleaned_data
        role.assigned_class = data["assigned_class"]
        role.all_sections = data["all_sections"]
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
        qs = Classes.objects.filter(semester=Semester.objects.get_active_semester())
        if self.q:
            qs = qs.filter(Q(course__subject__short_name__icontains=self.q) | Q(course__number__icontains=self.q) | Q(faculty__first_name__icontains=self.q) | Q(faculty__last_name__icontains=self.q)).all()
        return qs
    