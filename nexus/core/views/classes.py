from . import restrict_to_http_methods
from django.contrib.auth.decorators import login_required

@login_required
@restrict_to_http_methods('GET', 'POST')
def all_classes(request):
    pass

@restrict_to_http_methods('GET', 'POST')
def create_class(request):
    pass

@restrict_to_http_methods('GET', 'POST')
def class_details(request, class_id):
    pass

@restrict_to_http_methods('GET','POST')
def edit_class(request, class_id):
    pass

@restrict_to_http_methods('GET')
def list_class_times(request, class_id):
    pass

@restrict_to_http_methods('POST')
def add_class_time(request, class_id):
    pass

@restrict_to_http_methods('DELETE')
def delete_class_time(request, class_time_id):
    pass