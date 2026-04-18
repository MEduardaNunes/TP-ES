from django.urls import path
from . import views

app_name = "schedules"

urlpatterns = [
    path("main_calendar_view/", views.main_calendar_view, name="main_calendar_view"),
]