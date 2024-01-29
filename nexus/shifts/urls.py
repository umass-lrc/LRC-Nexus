from django.urls import path, re_path

from .views.users_shift import (
    users_shift,
    user_calendar,
    get_user_shifts,
    add_shift,
    edit_shift,
    add_edit_recurring,
    add_recurring,
    edit_recurring,
    record_meeting,
    UserAutocomplete,    
)

USERS_SHIFT_URLS = [
    path('users_shift/', users_shift, name='users_shift'),
    path('user_calender/<int:user_id>/', user_calendar, name='user_calendar'),
    path('user_calender/get_user_shifts/', get_user_shifts, name='get_user_shifts'),
    path('add_shift/<int:user_id>/', add_shift, name='add_shift'),
    path('edit_shift/<int:shift_id>/', edit_shift, name='edit_shift'),
    path('add_edit_recurring/<int:user_id>/', add_edit_recurring, name='add_edit_recurring'),
    path('add_recurring/<int:user_id>/', add_recurring, name='add_recurring'),
    path('edit_recurring/<int:rshift_id>/', edit_recurring, name='edit_recurring'),
    path('record_meeting/<int:user_id>/', record_meeting, name='record_meeting'),
    re_path(r'^users_shift/autocomplete/$', UserAutocomplete.as_view(), name='user-autocomplete'),
]

urlpatterns = (
    USERS_SHIFT_URLS
)
