from . import restrict_to_http_methods

@restrict_to_http_methods('GET', 'POST')
def create_course(request):
    pass

@restrict_to_http_methods('GET', 'POST')
def edit_course(request, course_id):
    pass

@restrict_to_http_methods('GET')
def list_courses(request):
    pass

@restrict_to_http_methods('GET')
def delete_course(request, course_id):
    pass