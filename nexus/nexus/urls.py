"""
URL configuration for nexus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, "home.html")

@login_required
def work_in_progress(request):
    return render(request, "work_in_progress_full_page.html")

# handler404 = 'core.views.handler404'

urlpatterns = [
    path('', index, name='index'),
    path('work_in_progress/', work_in_progress, name='work_in_progress'),
    path('admin/', admin.site.urls),
    path('explorer/', include('explorer.urls')),
    path('core/', include('core.urls')),
    path('users/', include('users.urls')),
    path('patches/', include('patches.urls')),
]
