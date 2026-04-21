from django.urls import path, include
from django.contrib import admin
from . import views

app_name = "schedules"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("conta/", include("accounts.urls")),
    path("main_calendar_view/", views.main_calendar_view, name="main_calendar_view"),
    path('logout/', views.logout_view, name='logout'),
    path("quick_create_activity/", views.quick_create_activity, name="quick_create_activity"),
    path("create/", views.create_schedule, name="create_schedule"),
    path("<int:schedule_id>/", views.view_schedule, name="view_schedule"),
    path("<int:schedule_id>/edit/", views.edit_schedule, name="edit_schedule"),
    path("<int:schedule_id>/delete/", views.delete_schedule, name="delete_schedule"),
    path("<int:schedule_id>/add_participant/", views.add_participant, name="add_participant"),
    path("<int:schedule_id>/remove_participant/", views.remove_participant, name="remove_participant"),
    path("<int:schedule_id>/create_activity/", views.create_activity, name="create_activity"),
    path("<int:schedule_id>/activity/<int:activity_id>/edit/", views.edit_activity, name="edit_activity"),
    path("<int:schedule_id>/activity/<int:activity_id>/delete/", views.delete_activity, name="delete_activity"),
    path("<int:schedule_id>/activity/<int:activity_id>/toggle_check/", views.toggle_check, name="toggle_check"),
]