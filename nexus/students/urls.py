from django.urls import path, re_path

from .views.payroll import (
    get_user_payroll_page,
    punch_in_out_position,
    sign_shift,
)


CALENDAR_URLS = [
    
]

PAYROLL_URLS = [
    path('payroll/', get_user_payroll_page, name='user_payroll'),
    path('payroll/punch-in-out/<int:position_id>/', punch_in_out_position, name='punch_in_out_position'),
    path('payroll/sign-shift/<int:shift_id>/', sign_shift, name='sign_shift'),
]

SCHEDULE_URLS = [
    
]

urlpatterns = (
    CALENDAR_URLS +
    PAYROLL_URLS +
    SCHEDULE_URLS
)
