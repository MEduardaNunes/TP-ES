from django.contrib import admin
from .models import UserThemePreference


@admin.register(UserThemePreference)
class UserThemePreferenceAdmin(admin.ModelAdmin):
	list_display = (
		"user",
		"accent_clr",
		"sidebar_gradient_start",
		"sidebar_gradient_end",
		"updated_at",
	)
	search_fields = ("user__username",)
