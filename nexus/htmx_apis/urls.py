from django.urls import path

from .views.schedule import (
    api_schedule_for_all_course,

)

SCHEDULE_URLS = [
    path("schedule/", api_schedule_for_all_course, name="api_schedule_for_all_course"),
]

urlpatterns = (
    SCHEDULE_URLS
)