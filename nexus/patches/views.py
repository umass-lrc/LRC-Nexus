from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from core.views import restrict_to_http_methods, restrict_to_groups

from users.models import (
    NexusUser,
    Positions,
)

from core.models import (
    Semester,
)

from .forms import (
    loadUsersForm,
    loadPositionsForm,
)

@login_required
@restrict_to_groups('Tech')
def load_users(request):
    if request.method == 'POST':
        form = loadUsersForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form error: {form.errors}")
            return render(request, 'load_users_response.html', context={'success': False})
        with open("temp/users.csv", "wb+") as f:
            for chunk in request.FILES['file'].chunks():
                f.write(chunk)
        return render(request, 'load_users_response.html', context={'success': True})
    form = loadUsersForm()
    context = {'form': form}
    return render(request, 'load_users.html', context)

@login_required
@restrict_to_http_methods('POST')
@restrict_to_groups('Tech')
def load_user_from_line(request, line_number):
    with open("temp/users.csv", "r") as f:
        to_read = None
        for i, line in enumerate(f):
            if i == line_number-1:
                to_read = line
                break
        if to_read is None:
            return HttpResponse("<b>==File End==</b><br/>")
        content = f"""
            <div
                hx-post="{reverse('load_user_from_line', kwargs={'line_number': line_number+1})}"
                hx-trigger="load"
                hx-target="this"
                hx-swap="outerHTML"
            >
            </div>
        """
        values = to_read.split(',')
        if len(values) != 3:
            content += f"<b>==Invalid Format On Line {line_number}==</b>"
        else:
            try:
                email = values[0].lower()
                first_name = values[1].title()
                if first_name[0] == '"':
                    first_name = first_name[1:-2]
                last_name = values[2].title()
                if last_name[0] == '"':
                    last_name = last_name[1:-2]
                user = NexusUser.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.set_unusable_password()
                user.save()
                content += f"<b>==User Added Successfully==</b>"
            except:
                content += f"<b>==Error Occoured On Line {line_number}, User Not Added==</b>"
        content += f"<br/>Line {line_number} Content: {to_read} <br/>"
        return HttpResponse(content)

@login_required
@restrict_to_groups('Tech')
def load_positions(request):
    if request.method == 'POST':
        form = loadPositionsForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, f"Form error: {form.errors}")
            return render(request, 'load_positions_response.html', context={'success': False})
        with open("temp/positions.csv", "wb+") as f:
            for chunk in request.FILES['file'].chunks():
                f.write(chunk)
        data = form.cleaned_data
        return render(request, 'load_positions_response.html', context={'success': True, 'position': data['position']})
    form = loadPositionsForm()
    context = {'form': form}
    return render(request, 'load_positions.html', context)

@login_required
@restrict_to_http_methods('POST')
@restrict_to_groups('Tech')
def load_position_from_line(request, line_number, position):
    with open("temp/positions.csv", "r") as f:
        to_read = None
        for i, line in enumerate(f):
            if i == line_number-1:
                to_read = line
                break
        print(to_read)
        if to_read is None:
            return HttpResponse("<b>==File End==</b><br/>")
        content = f"""
            <div
                hx-post="{reverse('load_position_from_line', kwargs={'line_number': line_number+1, 'position': position})}"
                hx-trigger="load"
                hx-target="this"
                hx-swap="outerHTML"
            >
            </div>
        """
        values = to_read.split(',')
        if len(values) != 2:
            content += f"<b>==Invalid Format On Line {line_number}==</b>"
        else:
            try:
                email = values[0].lower()
                hourly_pay = float(values[1])
                user = NexusUser.objects.get(email=email)
                Positions.objects.create(
                    user=user,
                    semester=Semester.objects.get_active_semester(),
                    position=position,
                    hourly_pay=hourly_pay,
                )
                content += f"<b>==Position Added Successfully==</b>"
            except Exception as e:
                content += f"<b>==Error Occoured On Line {line_number}, Position Not Added: {e}==</b>"
        content += f"<br/>Line {line_number} Content: {to_read} <br/>"
        return HttpResponse(content)