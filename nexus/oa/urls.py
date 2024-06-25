from django.urls import path, re_path

from .views.shift_request import (
    shift_requests,
    change_request,
    drop_request,
    add_request,
    add_request_form,
    change_request_form,
    drop_request_form,
)

SHIFT_REQUEST = [
    path('shift_requests/', shift_requests, name='oa_shift_requests'),
    path('add_request/<str:request_state>/', add_request, name='oa_add_request'),
    path('change_request/<str:request_state>/', change_request, name='oa_change_request'),
    path('drop_request/<str:request_state>/', drop_request, name='oa_drop_request'),
    path('add_request_form/<int:req_id>/', add_request_form, name='oa_add_request_form'),
    path('change_request_form/<int:req_id>/', change_request_form, name='oa_change_request_form'),
    path('drop_request_form/<int:req_id>/', drop_request_form, name='oa_drop_request_form'),
]

urlpatterns = (
    SHIFT_REQUEST
)
