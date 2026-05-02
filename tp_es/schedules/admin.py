from django.contrib import admin
from .models import Activity, ActivityCheck, Participant, Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
	list_display = ("name", "color", "icon_emoji", "created_at")
	search_fields = ("name",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
	list_display = ("title", "schedule", "kind", "activity_type", "priority", "date")
	list_filter = ("kind", "activity_type", "priority")
	search_fields = ("title", "schedule__name")


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
	list_display = ("schedule", "user", "role", "joined_at")
	list_filter = ("role",)
	search_fields = ("schedule__name", "user__username")


@admin.register(ActivityCheck)
class ActivityCheckAdmin(admin.ModelAdmin):
	list_display = ("activity", "user", "checked_at")
	search_fields = ("activity__title", "user__username")
