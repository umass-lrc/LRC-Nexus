from django.urls import path, re_path

from .views import page_not_found

from .views.faculty import (
    faculty_list,
    get_faculty_row,
    update_faculty_details,
    update_faculty_details_form,
    view_faculty_details,
    FacultyAutocomplete,
)

from .views.opportunities import (
    opportunities_list,
    get_opportunity_row,
    update_opportunity,
    update_opportunity_form,
    view_opportunity,
    create_opportunity_form,
    view_opportunity_full_page,
    delete_opportunity,
    OpportunityAutocomplete,
    KeywordAutocomplete,
)

from .views.search import (
    opportunity_search,
    search_no_result,
    opportunity_card,
)

from .views.check_opportunities import (
    check_opp_main,
    check_opp_row,
    check_opp_update_opportunity,
    check_opp_update_opportunity_form,
    check_opportunity_link,
    update_web_data,
    check_all_opportunity_links,
    check_opportunity_link_with_progress_bar,
    update_all_web_data,
    update_web_data_with_progress_bar,
    change_link_override,
    change_featured,
)



FACULTY_URLS = [
    path('faculty/', faculty_list, name='faculty_list'),
    path('faculty/<int:faculty_id>/', get_faculty_row, name='get_faculty_row'),
    path('update_faculty/<int:faculty_id>/', update_faculty_details, name='update_faculty_details'),
    path('update_faculty_form/<int:faculty_id>/', update_faculty_details_form, name='update_faculty_details_form'),
    path('view_faculty/<int:faculty_id>/', view_faculty_details, name='view_faculty_details'),
    re_path(r'^faculty/autocomplete/$', FacultyAutocomplete.as_view(), name='autocomplete-faculty'),
]

OPPORTUNITY_URLS = [
    path('opportunities/', opportunities_list, name='opportunities_list'),
    path('opportunities/<int:opp_id>/', get_opportunity_row, name='get_opportunity_row'),
    path('update_opportunity/<int:opp_id>/', update_opportunity, name='update_opportunity'),
    path('update_opportunity_form/<int:opp_id>/', update_opportunity_form, name='update_opportunity_form'),
    path('view_opportunity/<int:opp_id>/', view_opportunity, name='view_opportunity'),
    path('create_opportunity_form/', create_opportunity_form, name='create_opportunity_form'),
    path('view_opportunity_full_page/<int:opp_id>/', view_opportunity_full_page, name='view_opportunity_full_page'),
    re_path(r'^opportunity/autocomplete/$', OpportunityAutocomplete.as_view(), name='autocomplete-opportunity'),
    re_path(r'^keyword/autocomplete/$', KeywordAutocomplete.as_view(), name='autocomplete-keyword'),
    path('page_not_found/', page_not_found, name='opp_page_not_found'),
    path('delete_opportunity/<int:opp_id>/', delete_opportunity, name='delete_opportunity'),
]

CHECK_OPP_URLS = [
    path('check_opp_main/', check_opp_main, name='check_opp_main'),
    path('check_opp_row/<int:opp_id>/', check_opp_row, name='check_opp_row'),
    path('check_opp_update_opportunity/<int:opp_id>/', check_opp_update_opportunity, name='check_opp_update_opportunity'),
    path('check_opp_update_opportunity_form/<int:opp_id>/', check_opp_update_opportunity_form, name='check_opp_update_opportunity_form'),
    path('check_opportunity_link/<int:opp_id>/', check_opportunity_link, name='check_opportunity_link'),
    path('update_web_data/<int:opp_id>/', update_web_data, name='update_web_data'),
    path('check_all_opportunity_links/', check_all_opportunity_links, name='check_all_opportunity_links'),
    path('check_opportunity_link_with_progress_bar/<int:opp_id>/<int:max_id>/', check_opportunity_link_with_progress_bar, name='check_opportunity_link_with_progress_bar'),
    path('update_all_web_data/', update_all_web_data, name='update_all_web_data'),
    path('update_web_data_with_progress_bar/<int:opp_id>/<int:max_id>/', update_web_data_with_progress_bar, name='update_web_data_with_progress_bar'),
    path('change_link_override/<int:opp_id>/', change_link_override, name='change_link_override'),
    path('change_featured/<int:opp_id>/', change_featured, name='change_featured'),
]

SEARCH_URLS = [
    path('opportunity_search/', opportunity_search, name='opportunity_search'),
    path('search_no_result/', search_no_result, name='search_no_result'),
    path('opportunity_card/<int:opp_id>/', opportunity_card, name='opportunity_card'),
]

urlpatterns = (
    FACULTY_URLS +
    OPPORTUNITY_URLS +
    CHECK_OPP_URLS +
    SEARCH_URLS
)