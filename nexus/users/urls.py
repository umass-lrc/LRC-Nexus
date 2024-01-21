from django.urls import path

from .views.login import (
    login,
    logout,
)
from .views.users import (
    users,
    create_user,
    update_user,
    reset_password,
    get_user_row,
)

AUTH_URLS = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

]

USER_URLS = [
    path('users/', users, name='users'),
    path('users/create/', create_user, name='create_user'),
    path('users/update/<int:user_id>/', update_user, name='update_user'),
    path('users/reset_password/<int:user_id>/', reset_password, name='reset_password'),
    path('users/get_user_row/<int:user_id>/', get_user_row, name='get_user_row'),
]

urlpatterns = (
    AUTH_URLS +
    USER_URLS
)