from django.http import HttpResponseNotAllowed
from django.shortcuts import render

def restrict_to_http_methods(*methods):
    def decorator(func):
        def inner(request, *args, **kwargs):
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)
            return func(request, *args, **kwargs)
        return inner
    return decorator

def handler404(request, exception, template_name="404.html"):
    return render(request, template_name)