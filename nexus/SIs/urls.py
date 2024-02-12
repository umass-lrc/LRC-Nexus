from django.urls import path, re_path

from .views.role import (
    assign_role,
    update_role,
    ClassAutocomplete
)

from .views.schedule import (
    si_schedule_for_all_course
)

SI_ROLE_URLS = [
    path('assign_role/', assign_role, name='assign_role'),
    path('update_role/<int:role_id>/', update_role, name='update_role'),
    re_path(r'^class/autocomplete/$', ClassAutocomplete.as_view(), name='class-autocomplete'),
]

SCHEDULE_URLS = [
    path('schedule/', si_schedule_for_all_course, name='si_schedule_for_all_course'),
]   

urlpatterns = (
    SI_ROLE_URLS +
    SCHEDULE_URLS
)
