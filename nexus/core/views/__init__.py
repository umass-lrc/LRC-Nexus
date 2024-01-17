from django.http import HttpResponseNotAllowed

def restrict_to_http_methods(*methods):
    def decorator(func):
        def inner(request, *args, **kwargs):
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)
            return func(request, *args, **kwargs)
        return inner
    return decorator