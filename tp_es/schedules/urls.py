from django.urls import path, include
from django.contrib import admin
from . import views

app_name = "schedules"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("conta/", include("accounts.urls")),
    path("main_calendar_view/", views.main_calendar_view, name="main_calendar_view"),
]