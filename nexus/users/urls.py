from django.urls import path, re_path

from .views.login import (
    login,
    logout,
)
from .views.users import (
    users,
    search,
    create_user,
    update_user,
    reset_password,
    get_user_row,
    user_created,
    update_user_form,
)
from .views.positions import (
    positions,
    get_all_positions,
    add_position,
    delete_position,
    UserAutocomplete,
)
from .views.groups import (
    groups,
    create_group,
    create_group_form,
    delete_group,
    edit_group,
    add_group_member,
    remove_group_member,
    PositionAutocomplete,
)

AUTH_URLS = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

]

USER_URLS = [
    path('users/', users, name='users'),
    path('users/search', search, name='search_users'),
    path('users/create/', create_user, name='create_user'),
    path('users/update/<int:user_id>/', update_user, name='update_user'),
    path('users/reset_password/<int:user_id>/', reset_password, name='reset_password'),
    path('users/get_user_row/<int:user_id>/', get_user_row, name='get_user_row'),
    path('users/user_created/<int:user_id>/', user_created, name='user_created'),
    path('users/update_user_form/<int:user_id>/', update_user_form, name='update_user_form'),
]

POSITION_URLS = [
    path('positions/', positions, name='positions'),
    path('positions/<int:semester_id>/<int:position>/', get_all_positions, name='get_all_positions'),
    path('positions/add_position_default/', add_position, name='add_position_default'),
    path('positions/add_position/<int:semester_id>/<int:position_id>/', add_position, name='add_position'),
    path('positions/delete/<int:position_id>/', delete_position, name='delete_position'),
    re_path(r'^positions/autocomplete/users/$', UserAutocomplete.as_view(), name='user_autocomplete'),
]

GROUP_URLS = [
    path('groups/', groups, name='groups'),
    path('groups/create/', create_group, name='create_group'),
    path('groups/create_form/', create_group_form, name='create_group_form'),
    path('groups/delete/<int:group_id>/', delete_group, name='delete_group'),
    path('groups/edit/<int:group_id>/', edit_group, name='edit_group'),
    path('groups/add_member/<int:group_id>/', add_group_member, name='add_group_member'),
    path('groups/remove_member/<int:group_id>/<int:member_id>/', remove_group_member, name='remove_group_member'),
    re_path(r'^groups/autocomplete/position/$', PositionAutocomplete.as_view(), name='position_autocomplete'),
]

urlpatterns = (
    AUTH_URLS +
    USER_URLS +
    POSITION_URLS +
    GROUP_URLS 
)
