from . import restrict_to_http_methods

@restrict_to_http_methods('GET', 'POST')
def create_building(request):
    pass

@restrict_to_http_methods('GET', 'POST')
def edit_building(request):
    pass

@restrict_to_http_methods('GET')
def list_buildings(request):
    pass

@restrict_to_http_methods('DELETE')
def delete_building(request, building_id):
    pass