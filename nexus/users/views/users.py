from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from core.views import restrict_to_http_methods

from ..models import (
    NexusUser,
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
    pass

@login_required
@restrict_to_http_methods('GET', 'POST')
def update_user(request, user_id):
    pass