from . import restrict_to_http_methods

@restrict_to_http_methods('GET', 'POST')
def create_faculty(request):
    pass

@restrict_to_http_methods('GET', 'POST')
def edit_faculty(request):
    pass

@restrict_to_http_methods('GET')
def list_faculties(request):
    pass

@restrict_to_http_methods('DELETE')
def delete_faculty(request, faculty_id):
    pass