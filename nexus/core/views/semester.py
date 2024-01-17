from . import restrict_to_http_methods

@restrict_to_http_methods('GET', 'POST')
def create_semester(request):
    pass

@restrict_to_http_methods('GET')
def semester_details(request, semester_id):
    pass

@restrict_to_http_methods('GET')
def list_holidays(request, semester_id):
    pass

@restrict_to_http_methods('POST')
def add_holiday(request, semester_id):
    pass

@restrict_to_http_methods('GET')
def list_day_switches(request, semester_id):
    pass

@restrict_to_http_methods('POST')
def add_day_switch(request, semester_id):
    pass

@restrict_to_http_methods('GET')
def list_semesters(request):
    pass

@restrict_to_http_methods('PUT')
def change_active_semester(request, semester_id):
    pass