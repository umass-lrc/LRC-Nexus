from django.urls import path

from .views.schedule import (
    api_si_schedule_for_all_course,
    api_tutor_schedule_for_all_course,

)

SCHEDULE_URLS = [
    path("tutor_schedule/", api_tutor_schedule_for_all_course, name="api_tutor_schedule_for_all_course"),
    path("si_schedule/", api_si_schedule_for_all_course, name="api_si_schedule_for_all_course"),
]

urlpatterns = (
    SCHEDULE_URLS
)