from datetime import datetime
from django.urls import path, re_path, register_converter

from .views.payroll import (
    get_user_payroll_page,
    get_user_punch_in_out,
    individual_punch_in_out,
    punch_in_out_position,
    shift_punch_in_out,
    get_attendance_for_shifts,
    attendance_for_shift,
    get_approve_entire_weeks,
    approve_entire_week,
    get_user_payslips,
    get_payslip_for,
)

from .views.calendar import (
    student_calendar,
    get_student_shifts,
    get_student_calendar,
    add_shift_request,
    change_or_drop_shift_request,
    change_shift_request,
    drop_shift_request,
    add_shift_request_display,
)


class DateConverter:
    regex = '\d{4}-\d{1,2}-\d{1,2}'
    format = '%Y-%m-%d'

    def to_python(self, value):
        return datetime.strptime(value, self.format).date()

    def to_url(self, value):
        return value.strftime(self.format)

register_converter(DateConverter, 'date')

CALENDAR_URLS = [
    path('calendar/', student_calendar, name='student_calendar'),
    path('calendar/get-student-calendar/', get_student_calendar, name='get_student_calendar'),
    path('calendar/get-student-shifts/', get_student_shifts, name='get_student_shifts'),
    path('calendar/add-shift-request/', add_shift_request, name='add_shift_request'),
    path('calendar/change-or-drop-shift-request/<int:shift_id>/', change_or_drop_shift_request, name='change_or_drop_shift_request'),
    path('calendar/change-shift-request/<int:shift_id>/', change_shift_request, name='change_shift_request'),
    path('calendar/drop-shift-request/<int:shift_id>/', drop_shift_request, name='drop_shift_request'),
    path('calendar/add-shift-request-display/<int:req_id>/', add_shift_request_display, name='add_shift_request_display'),
]

PAYROLL_URLS = [
    path('payroll/', get_user_payroll_page, name='get_user_payroll_page'),
    path('payroll/punch-in-out/', get_user_punch_in_out, name='get_user_punch_in_out'),
    path('payroll/individual-punch-in-out/<int:position_id>/', individual_punch_in_out, name='individual_punch_in_out'),
    path('payroll/punch-in-out-position/<int:position_id>/', punch_in_out_position, name='punch_in_out_position'),
    path('payroll/shift-punch-in-out/<int:shift_id>/', shift_punch_in_out, name='shift_punch_in_out'),
    path('payroll/get-attendance-for-shifts/', get_attendance_for_shifts, name='get_attendance_for_shifts'),
    path('payroll/attendance-for-shift/<int:shift_id>/', attendance_for_shift, name='attendance_for_shift'),
    path('payroll/get-approve-entire-weeks/', get_approve_entire_weeks, name='get_approve_entire_weeks'),
    path('payroll/approve-entire-week/<date:week_end>/', approve_entire_week, name='approve_entire_week'),
    path('payroll/get-user-payslips/', get_user_payslips, name='get_user_payslips'),
    path('payroll/get-payslip-for/<date:week_end>/', get_payslip_for, name='get_payslip_for'),
]

SCHEDULE_URLS = [
]

urlpatterns = (
    CALENDAR_URLS +
    PAYROLL_URLS +
    SCHEDULE_URLS
)
