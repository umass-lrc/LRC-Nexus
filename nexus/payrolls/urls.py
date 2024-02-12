from django.urls import path, re_path

from .views.weekly import (
    weekly_payroll,
    all_weekly_payroll,
    single_weekly_payroll,
)

WEEKLY_PAYROLL_URLS = [
    path('weekly_payroll/', weekly_payroll, name='weekly_payroll'),
    path('all_weekly_payroll/', all_weekly_payroll, name='all_weekly_payroll'),
    path('single_weekly_payroll/<int:payroll_id>/', single_weekly_payroll, name='single_weekly_payroll'),
]

NOT_SIGNED_PAYROLL_URLS = [
]

STUDENT_REPORT_URLS = [
    
]

urlpatterns = (
    WEEKLY_PAYROLL_URLS +
    NOT_SIGNED_PAYROLL_URLS +
    STUDENT_REPORT_URLS
)