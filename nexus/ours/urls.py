from django.urls import path, re_path

from .views.faculty import (
    faculty_list,
    get_faculty_row,
    update_faculty_details,
    update_faculty_details_form,
    view_faculty_details,
)

from .views.opportunities import (
    opportunities_list,
    get_opportunity_row,
    update_opportunity,
    update_opportunity_form,
    view_opportunity,
    create_opportunity_form,
)


FACULTY_URLS = [
    path('faculty/', faculty_list, name='faculty_list'),
    path('faculty/<int:faculty_id>/', get_faculty_row, name='get_faculty_row'),
    path('update_faculty/<int:faculty_id>/', update_faculty_details, name='update_faculty_details'),
    path('update_faculty_form/<int:faculty_id>/', update_faculty_details_form, name='update_faculty_details_form'),
    path('view_faculty/<int:faculty_id>/', view_faculty_details, name='view_faculty_details'),
]

OPPORTUNITY_URLS = [
    path('opportunities/', opportunities_list, name='opportunities_list'),
    path('opportunities/<int:opp_id>/', get_opportunity_row, name='get_opportunity_row'),
    path('update_opportunity/<int:opp_id>/', update_opportunity, name='update_opportunity'),
    path('update_opportunity_form/<int:opp_id>/', update_opportunity_form, name='update_opportunity_form'),
    path('view_opportunity/<int:opp_id>/', view_opportunity, name='view_opportunity'),
    path('create_opportunity_form/', create_opportunity_form, name='create_opportunity_form'),
]

SEARCH_URLS = []

urlpatterns = (
    FACULTY_URLS +
    OPPORTUNITY_URLS +
    SEARCH_URLS
)