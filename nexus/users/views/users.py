from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SearchUserForm
from ..models import NexusUser

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
    users = NexusUser.objects.all()
    context = {'users': users}
    return render(request, 'users.html', context)

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

def basic_search(self, search_query):
        search_query = search_query.strip()
        search_query_list = []
        i = 0
        # Parse the search query to handle quotes and spaces
        while i < len(search_query):
            if search_query[i] == '"':
                start = i
                i += 1
                while i < len(search_query) and search_query[i] != '"':
                    i += 1
                search_query_list.append(search_query[start + 1:i])
                i += 1
            elif search_query[i] == ' ':
                i += 1
            else:
                start = i
                while i < len(search_query) and search_query[i] != ' ':
                    i += 1
                search_query_list.append(search_query[start:i])
        
        # Remove any empty strings from the search list
        search_query_list = [query for query in search_query_list if query != '']
        
        # Build the filter query list for user-related fields
        filter_query = [
            (
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) 
            ) if query not in ['AND', 'OR'] else query 
            for query in search_query_list 
        ]
        
        final_query = None
        i = 0    
        # Process the filter query list with AND/OR logic
        while i < len(filter_query):
            if final_query is None:
                if filter_query[i] not in ['AND', 'OR']:
                    final_query = filter_query[i]
            elif filter_query[i] in ['AND', 'OR']:
                j = i + 1
                while j < len(filter_query) and filter_query[j] in ['AND', 'OR']:
                    j += 1
                if j < len(filter_query):
                    final_query = final_query & filter_query[j] if filter_query[i] == 'AND' else final_query | filter_query[j]
                i = j
            else:
                final_query = final_query & filter_query[i]
            i += 1
        
        # Return the filtered queryset of users
        return self.all().filter(final_query).distinct()


def search_user(request):
    form = SearchUserForm(request.GET or None)
    users = NexusUser.objects.none()
    if form.is_valid():
        query = form.cleaned_data.get('query', '')
        if query:
            # You can adjust the search logic here to match your requirements.
            users = NexusUser.objects.filter(first_name__icontains=query)  # Example filter

    return render(request, 'search_user.html', {'form': form, 'users': users})
