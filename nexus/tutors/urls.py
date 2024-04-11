from django.urls import path, re_path

from .views.role import (
    assign_role,
    update_role,
    CourseAutocomplete,
)

from .views.schedule import (
    tutor_schedule_for_all_course,
)

from .views.shift_request import (
    shift_requests,
    change_request,
    add_request,
    drop_request,
    change_request_form,
    add_request_form,
    drop_request_form,
)

ROLE_URLS = [
    path('assign-role/', assign_role, name='tutor_assign_role'),
    path('update-role/<int:role_id>/', update_role, name='tutor_update_role'),
    re_path(r'^course/autocomplete/$', CourseAutocomplete.as_view(), name='course-autocomplete'),
]

SCHEDULE_URLS = [
    path('schedule/', tutor_schedule_for_all_course, name='tutor_schedule_for_all_course'),
]

SHIFT_REQUEST = [
    path('shift-requests/', shift_requests, name='tutor_shift_requests'),
    path('add-request/<str:request_state>/', add_request, name='tutor_add_request'),
    path('change-request/<str:request_state>/', change_request, name='tutor_change_request'),
    path('drop-request/<str:request_state>/', drop_request, name='tutor_drop_request'),
    path('add-request-form/<int:req_id>/', add_request_form, name='tutor_add_request_form'),
    path('change-request-form/<int:req_id>/', change_request_form, name='tutor_change_request_form'),
    path('drop-request-form/<int:req_id>/', drop_request_form, name='tutor_drop_request_form'),
]

urlpatterns = (
    ROLE_URLS +
    SCHEDULE_URLS +
    SHIFT_REQUEST
)
