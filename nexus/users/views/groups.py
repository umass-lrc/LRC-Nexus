import json
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.db.models import Q

from dal import autocomplete

from core.views import restrict_to_http_methods

from core.models import (
    Semester,
)

from ..models import (
    NexusUser,
    PositionGroups,
    Positions,
)

from ..forms.groups import (
    CreateGroupForm,
    AddGroupMemeberForm,
)

@login_required
@restrict_to_http_methods('GET')
def groups(request):
    pgs = PositionGroups.objects.filter(semester=Semester.objects.get_active_semester()).all()
    pgs_data = []
    for pg in pgs:
        pgs_data.append({
            'id': pg.id,
            'name': pg.name,
            'count': pg.members.count(),
        })
    form = CreateGroupForm()
    context = {'form': form, 'pgs': pgs_data}
    return render(request, 'groups_main.html', context)

@login_required
@restrict_to_http_methods('POST')
def create_group(request):
    form = CreateGroupForm(request.POST)
    if not form.is_valid():
        messages.error(request, f'Form Errors: {form.errors}')
        return render(request, 'group_response.html', context={'success': False})
    data = form.cleaned_data
    try:
        pg = PositionGroups.objects.create(name=data['name'], semester=Semester.objects.get_active_semester())
        pg.save()
    except:
        messages.error(request, 'Group with same name already exits.')
        return render(request, 'group_response.html', context={'success': False})
    
    messages.success(request, 'Group created successfully.')
    print(pg.members.count())
    pg = {
        'id': pg.id,
        'name': pg.name,
        'count': pg.members.count(),
    }
    context = {'success': True, 'pg': pg}
    return render(request, 'group_response.html', context)

@login_required
@restrict_to_http_methods('GET')
def create_group_form(request):
    form = CreateGroupForm()
    context = {'form': form}
    return render(request, 'just_form.html', context)

@login_required
@restrict_to_http_methods('DELETE')
def delete_group(request, group_id):
    pg = PositionGroups.objects.get(id=group_id)
    pg.delete()
    response = HttpResponse()
    response["HX-Trigger"] = json.dumps({"deleteGroup": f"gt-{group_id}"})
    return response

@login_required
@restrict_to_http_methods('GET')
def edit_group(request, group_id):
    group = PositionGroups.objects.get(id=group_id)
    form = AddGroupMemeberForm(group_id)
    context = {'form': form, 'group': group}
    return render(request, 'edit_group_response.html', context)

@login_required
@restrict_to_http_methods('POST')
def add_group_member(request, group_id):
    form = AddGroupMemeberForm(group_id, request.POST)
    if not form.is_valid():
        messages.error(request, f'Form Errors: {form.errors}')
        return render(request, 'add_member_response.html', context={'success': False})
    data = form.cleaned_data
    pg = PositionGroups.objects.get(id=group_id)
    if data['member'] in pg.members.all():
        messages.error(request, 'Member already added.')
        return render(request, 'add_member_response.html', context={'success': False})
    pg.members.add(data['member'])
    pg.save()
    messages.success(request, 'Member added successfully.')
    context = {'success': True, 'member': data['member'], 'group_id': group_id}
    response = render(request, 'add_member_response.html', context)
    response["HX-Trigger"] = json.dumps({"changeMemberCount": f"gt-{group_id},{pg.members.count()}"})
    return response

@login_required
@restrict_to_http_methods('DELETE')
def remove_group_member(request, group_id, member_id):
    pg = PositionGroups.objects.get(id=group_id)
    member = Positions.objects.get(id=member_id)
    pg.members.remove(member)
    pg.save()
    response = HttpResponse()
    response["HX-Trigger"] = json.dumps({"changeMemberCount": f"gt-{group_id},{pg.members.count()}", "deleteMember": f"mt-{member_id}"})
    return response

class PositionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        active_semester = Semester.objects.get_active_semester()
        qs = Positions.objects.filter(semester=active_semester).all()
        if self.q:
            qs = qs.filter(Q(user__first_name__icontains=self.q) | Q(user__last_name__icontains=self.q)).all()
        return qs