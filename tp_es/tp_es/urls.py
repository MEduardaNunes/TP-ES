"""
URL configuration for tp_es project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from planify.views import home, calendar, user_space, register, login_user, logout_user, edit_user, delete_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('calendar/', calendar, name='calendar'),
    path('user/', user_space, name='user_space'),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("edit-user/", edit_user, name="edit_user"),
    path("delete-user/", delete_user, name="delete_user"),
]
