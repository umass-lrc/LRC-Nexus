from django.urls import path

from .views import (
    load_users,
    load_user_from_line,
    load_positions,
    load_position_from_line,
)

urlpatterns = [
    path('load_users/', load_users, name='load_users'),
    path('load_users/load_user_from_line/<int:line_number>/', load_user_from_line, name='load_user_from_line'),
    path('load_positions/', load_positions, name='load_positions'),
    path('load_positions/load_position_from_line/<int:line_number>/<int:position>/', load_position_from_line, name='load_position_from_line'),
]