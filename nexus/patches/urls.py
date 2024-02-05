from django.urls import path

from .views import (
    load_users,
    load_user_from_line,
    load_positions,
    load_position_from_line,
    load_courses,
    load_course_from_line,
    load_faculties,
    load_faculty_from_line,
    load_classes,
    load_class_from_line,
    fix_payroll,
)

urlpatterns = [
    path('load_users/', load_users, name='load_users'),
    path('load_users/load_user_from_line/<int:line_number>/', load_user_from_line, name='load_user_from_line'),
    path('load_positions/', load_positions, name='load_positions'),
    path('load_positions/load_position_from_line/<int:line_number>/<int:position>/', load_position_from_line, name='load_position_from_line'),
    path('load_courses/', load_courses, name='load_courses'),
    path('load_courses/load_course_from_line/<int:line_number>/', load_course_from_line, name='load_course_from_line'),
    path('load_faculties/', load_faculties, name='load_faculties'),
    path('load_faculties/load_faculty_from_line/<int:line_number>/', load_faculty_from_line, name='load_faculty_from_line'),
    path('load_classes/', load_classes, name='load_classes'),
    path('load_classes/load_class_from_line/<int:line_number>/', load_class_from_line, name='load_class_from_line'),
    path('fix_payroll/', fix_payroll, name='fix_payroll')
]