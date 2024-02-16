from django.urls import path, re_path

from .views.role import (
    assign_role,
    update_role,
    CourseAutocomplete,
)

from .views.schedule import (
    tutor_schedule_for_all_course,
)

ROLE_URLS = [
    path('assign-role/', assign_role, name='tutor_assign_role'),
    path('update-role/<int:role_id>/', update_role, name='tutor_update_role'),
    re_path(r'^course/autocomplete/$', CourseAutocomplete.as_view(), name='course-autocomplete'),
]

SCHEDULE_URLS = [
    path('schedule/', tutor_schedule_for_all_course, name='tutor_schedule_for_all_course'),
]

urlpatterns = (
    ROLE_URLS +
    SCHEDULE_URLS
)
