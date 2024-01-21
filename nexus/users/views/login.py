from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout as django_logout, password_validation
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from core.views import restrict_to_http_methods

from ..forms.login import (
    LogInForm,
)

from ..models import (
    NexusUser,
)

@restrict_to_http_methods('GET', 'POST')
def login(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, f"Form errors: {form.errors}")
            context = {'message_form_id': 'login_form_message'} 
            return render(request, 'alerts.html', context)
        data = form.cleaned_data
        try:
            user = NexusUser.objects.get(email=data['email'])
            if not user.has_usable_password():
                try:
                    password_validation.validate_password(data['password'], user)
                    user.set_password(data['password'])
                    user.save()
                    messages.add_message(request, messages.SUCCESS, "Password successfully set! Password you just set is your new password.")
                except ValidationError as errors:
                    html = "<br/><br/><ul>"
                    for e in errors:
                        html += f"<li>{e}</li>"
                    html += "</ul>"
                    messages.add_message(request, messages.ERROR, f"Error while setting your new password: {html}")
                    context = {'message_form_id': 'login_form_message'} 
                    return render(request, 'alerts.html', context)
        except NexusUser.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Email or Password is incorrect.")
            context = {'message_form_id': 'login_form_message'} 
            return render(request, 'alerts.html', context)
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            messages.add_message(request, messages.ERROR, "Email or Password is incorrect.")
            context = {'message_form_id': 'login_form_message'} 
            return render(request, 'alerts.html', context)
        django_login(request, user)
        response = HttpResponse()
        response["HX-Redirect"] = request.GET.get('next', reverse('index'))
        return response
    context = {
        'title': 'Log In',
        'form': LogInForm(),
        'post_url': 'login',
        'next': request.GET.get('next', None),
    }
    return render(request, 'login.html', context)

@login_required
@restrict_to_http_methods('GET')
def logout(request):
    django_logout(request)
    return redirect('login')