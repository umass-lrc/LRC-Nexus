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
    delete_class_shifts,
    load_tutor_roles,
    load_tutor_role_from_line,
    delete_error_drop_req,
    load_faculty_positions,
    load_faculty_position_from_line,
    load_ours_opportunities,
    load_ours_opportunity_from_line,
    load_majors,
    load_major_from_line,
    list_all_duplicate_opportunities,
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
    path('fix_payroll/', fix_payroll, name='fix_payroll'),
    path('delete_class_shifts/', delete_class_shifts, name='delete_class_shifts'),
    path('load_tutor_roles/', load_tutor_roles, name='load_tutor_roles'),
    path('load_tutor_roles/load_tutor_role_from_line/<int:line_number>/', load_tutor_role_from_line, name='load_tutor_role_from_line'),
    path('delete_error_drop_req/', delete_error_drop_req, name='delete_error_drop_req'),
    path('load_faculty_positions/', load_faculty_positions, name='load_faculty_positions'),
    path('load_faculty_positions/load_faculty_position_from_line/<int:line_number>/', load_faculty_position_from_line, name='load_faculty_position_from_line'),
    path('load_ours_opportunities/', load_ours_opportunities, name='load_ours_opportunities'),
    path('load_ours_opportunities/load_ours_opportunity_from_line/<int:line_number>/', load_ours_opportunity_from_line, name='load_ours_opportunity_from_line'),
    path('load_majors/', load_majors, name='load_majors'),
    path('load_majors/load_major_from_line/<int:line_number>/', load_major_from_line, name='load_major_from_line'),
    path('list_all_duplicate_opportunities/', list_all_duplicate_opportunities, name='list_all_duplicate_opportunities'),
]