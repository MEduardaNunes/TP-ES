from .models import UserThemePreference


def ui_preferences(request):
    if not request.user.is_authenticated:
        return {}

    preference, _ = UserThemePreference.objects.get_or_create(user=request.user)
    return {
        "ui_theme": preference,
        "ui_icons": preference,
    }
