from django.urls import path, re_path

from .views.role import (
    assign_role,
    update_role,
    ClassAutocomplete
)

SI_ROLE_URLS = [
    path('assign_role/', assign_role, name='assign_role'),
    path('update_role/<int:role_id>/', update_role, name='update_role'),
    re_path(r'^class/autocomplete/$', ClassAutocomplete.as_view(), name='class-autocomplete'),
]

urlpatterns = (
    SI_ROLE_URLS
)
