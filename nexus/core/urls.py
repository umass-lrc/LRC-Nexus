from django.urls import path

from .views.semester import (
    create_semester,
    semester_details,
    list_holidays,
    add_holiday,
    list_day_switches,
    add_day_switch,
    list_semesters,
    change_active_semester,
)

from .views.faculty import (
    create_faculty,
    list_faculties,
    edit_faculty,
)

SEMESTER_URLS = [
    path('semester/create/', create_semester, name='create_semester'),
    path('semester/details/<int:semester_id>/', semester_details, name='semester_details'),
    path('semester/holidays/<int:semester_id>/', list_holidays, name='list_holidays'),
    path('semester/day_switchs/<int:semester_id>/', list_day_switches, name='list_day_switches'),
    path('semester/holiday/add/<int:semester_id>/', add_holiday, name='add_holiday'),
    path('semester/day_switch/add/<int:semester_id>/', add_day_switch, name='add_day_switch'),
    path('semester/list/', list_semesters, name='list_semesters'),
    path('semester/change_active/<int:semester_id>/', change_active_semester, name='change_active_semester')
]

FACULTY_URLS = [
    path('faculty/create/', create_faculty, name='create_faculty'),
    path('faculty/list/', list_faculties, name='list_faculties'),
    path('faculty/edit/<int:faculty_id>/', edit_faculty, name='edit_faculty'),
]

BUILDING_URLS = [

]

COURSE_URLS = [

]

CLASSES_URLS = [

]

urlpatterns = (
    SEMESTER_URLS +
    FACULTY_URLS +
    BUILDING_URLS +
    COURSE_URLS +
    CLASSES_URLS
)
