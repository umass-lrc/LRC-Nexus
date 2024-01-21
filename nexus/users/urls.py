from django.urls import path

from .views.login import (
    login,
    logout,
)
from .views.users import (
    users,
    create_user,
    update_user,
)

AUTH_URLS = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

]

USER_URLS = [
    path('users/', users, name='users'),
    path('users/create/', create_user, name='create_user'),
    path('users/update/<int:user_id>/', update_user, name='update_user'),
]

urlpatterns = (
    AUTH_URLS +
    USER_URLS
)