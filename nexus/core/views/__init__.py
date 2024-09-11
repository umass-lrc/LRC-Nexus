from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect

def restrict_to_http_methods(*methods):
    def decorator(func):
        def inner(request, *args, **kwargs):
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)
            return func(request, *args, **kwargs)
        return inner
    return decorator

def restrict_to_groups(*groups):
    def decorator(func):
        def inner(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            not_in_group = not request.user.groups.filter(name__in=groups).exists()
            staff_group = [group for group in groups if group.startswith('Staff')]
            not_in_staff_group = True
            if "Staff-OURS-Mentor" in staff_group:
                not_in_staff_group = not_in_staff_group and not request.user.is_ours_mentor()
            elif "Staff-OA" in staff_group:
                not_in_staff_group = not_in_staff_group and not request.user.is_oa()
            if not_in_group and not_in_staff_group and not request.user.is_superuser:
                response = render(request, '403.html')
                response.status_code = 403
                return response
            return func(request, *args, **kwargs)
        return inner
    return decorator

def handler404(request, exception, template_name="404.html"):
    response = render(request, template_name)
    response.status_code = 404
    return response