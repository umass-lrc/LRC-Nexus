from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from core.views import restrict_to_http_methods
from django.db.models import Value
from django.db.models.functions import Concat

from ..models import (
    NexusUser,
)

from ..forms.users import (
    CreateUserForm,
)

@login_required
@restrict_to_http_methods('GET')
def users(request):
    users = NexusUser.objects.all()
    context = {'users': users}
    return render(request, 'users.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
def create_user(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if not form.is_valid():
            messages.error(request, f'Form Errors: {form.errors}')
            return render(request, 'alerts.html', status=202)
        data = form.cleaned_data
        data['first_name'] = data['first_name'].title()
        data['last_name'] = data['last_name'].title()
        data['email'] = data['email'].lower()
        user = NexusUser.objects.create_user(**data)
        user.set_unusable_password()
        user.save()
        form = CreateUserForm()
        context = {'form': form, 'success': True, 'new_user': user}
        messages.success(request, 'User created successfully.')
        return render(request, 'create_user.html', context)
    form = CreateUserForm()
    context = {'form': form, 'success': False}
    return render(request, 'create_user.html', context)

@login_required
@restrict_to_http_methods('GET', 'POST')
def update_user(request, user_id):
    pass

@login_required
@restrict_to_http_methods('GET')
def get_user_row(request, user_id):
    user = NexusUser.objects.get(id=user_id)
    context = {'curr_user': user}
    return render(request, 'user_row.html', context)

@login_required
@restrict_to_http_methods('GET')
def reset_password(request, user_id):
    user = NexusUser.objects.get(id=user_id)
    user.set_unusable_password()
    user.save()
    return redirect('get_user_row', user_id=user_id)