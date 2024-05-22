from django.urls import path

from .views.schedule import (
    api_si_schedule_for_all_course,
    api_tutor_schedule_for_all_course,
)

from .views.opportunity_search import (
    opportunity_search,
    search_no_result,
    opportunity_card,
    opportunity_details,
)

SCHEDULE_URLS = [
    path("tutor_schedule/", api_tutor_schedule_for_all_course, name="api_tutor_schedule_for_all_course"),
    path("si_schedule/", api_si_schedule_for_all_course, name="api_si_schedule_for_all_course"),
]

OPP_SEARCH_URLS = [
    path("search/", opportunity_search, name="api_opportunity_search"),
    path("search_no_result/", search_no_result, name="api_search_no_result"),
    path("opportunity_card/<int:opp_id>/", opportunity_card, name="api_opportunity_card"),
    path("opportunity_details/<int:opp_id>/", opportunity_details, name="api_opportunity_details"),
]

urlpatterns = (
    SCHEDULE_URLS +
    OPP_SEARCH_URLS
)