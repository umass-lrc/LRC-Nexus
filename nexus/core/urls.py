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

from .views.building import (
    create_building,
    list_buildings,
    edit_building,
)

from .views.course import (
    create_course,
    list_courses,
    edit_course,
)

from .views.classes import (
    all_classes,
    create_class,
    edit_class,
    add_class_time,
    delete_class_time,
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
    path('building/create/', create_building, name='create_building'),
    path('building/list/', list_buildings, name='list_buildings'),
    path('building/edit/<str:building_short_name>/', edit_building, name='edit_building'),
]

COURSE_URLS = [
    path('course/create/', create_course, name='create_course'),
    path('course/list/', list_courses, name='list_courses'),
    path('course/edit/<int:course_id>/', edit_course, name='edit_course'),
]

CLASSES_URLS = [
    path('classes/all/', all_classes, name='all_classes'),
    path('classes/create/<int:semester_id>/', create_class, name='create_class'),
    path('classes/edit/<int:class_id>/', edit_class, name='edit_class'),
    path('classes/add_time/<int:class_id>/', add_class_time, name='add_class_time'),
    path('classes/delete_time/<int:class_time_id>/', delete_class_time, name='delete_class_time'),
]

urlpatterns = (
    SEMESTER_URLS +
    FACULTY_URLS +
    BUILDING_URLS +
    COURSE_URLS +
    CLASSES_URLS
)
