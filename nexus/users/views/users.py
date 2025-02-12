from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from core.views import restrict_to_http_methods, restrict_to_groups

import json

from ..models import (
    NexusUser,
)

from ..forms.users import (
    CreateUserForm,
    UpdateUserForm,
)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def users(request):
    return render(request, 'users.html')

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def search(request):
    search = request.GET.get('q')
    if search:
        users = NexusUser.objects.filter(Q(first_name__icontains=search)|Q(last_name__icontains=search)|Q(email__icontains=search))
    else:
        users = NexusUser.objects.all()
    context = {'users': users}
    return render(request, 'users_search.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def create_user(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'alerts.html')
        data = form.cleaned_data
        data['first_name'] = data['first_name'].title()
        data['last_name'] = data['last_name'].title()
        data['email'] = data['email'].lower()
        user = NexusUser.objects.create_user(**data)
        user.set_unusable_password()
        user.save()
        form = CreateUserForm()
        context = {'success': True, 'new_user_id': user.id, 'type': 'create'}
        messages.success(request, 'User created successfully.')
        return render(request, 'create_user.html', context)
    form = CreateUserForm()
    context = {'form': form, 'success': False}
    response = render(request, 'create_user.html', context)
    response["HX-Trigger-After-Settle"] = "userFormRefreshed"
    return response

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def user_created(request, user_id):
    form = CreateUserForm()
    user = NexusUser.objects.get(id=user_id)
    context = {'new_user': user, 'form': form, 'success': True, 'type': 'after_create'}
    response = render(request, 'create_user.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"userCreated": f"ut-{user.id}"})
    return response

@login_required
@restrict_to_http_methods('GET', 'POST')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def update_user(request, user_id):
    user = NexusUser.objects.get(id=user_id)
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'alerts.html')
        data = form.cleaned_data
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.save()
        messages.success(request, 'User updated successfully.')
        context = {'success': True, 'curr_user': user}
        return render(request, 'update_user.html', context)
    context = {'success':False, 'curr_user': user}
    response = render(request, 'update_user.html', context)
    response["HX-Trigger-After-Settle"] = json.dumps({"userUpdateClicked": f"ut-{user.id}"})
    return response

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def update_user_form(request, user_id):
    user = NexusUser.objects.get(id=user_id)
    form = UpdateUserForm(instance=user)
    context = {'form': form}
    return render(request, 'just_form.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def get_user_row(request, user_id):
    user = NexusUser.objects.get(id=user_id)
    context = {'curr_user': user}
    return render(request, 'user_row.html', context)

@login_required
@restrict_to_http_methods('GET')
@restrict_to_groups('Staff Admin', 'SI Supervisor', 'Tutor Supervisor', 'OURS Supervisor')
def reset_password(request, user_id):
    loged_in_user = request.user
    user = NexusUser.objects.get(id=user_id)
    if user.id != loged_in_user.id:
        user.set_unusable_password()
        user.save()
    return redirect('get_user_row', user_id=user_id)