from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


hex_color_validator = RegexValidator(
	regex=r"^#[0-9A-Fa-f]{6}$",
	message="A cor deve ser um código hexadecimal válido (ex: #FF0000).",
	code="invalid_color",
)


class UserThemePreference(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="theme_preference",
	)

	base_clr = models.CharField(max_length=7, default="#f8f9ff", validators=[hex_color_validator])
	line_clr = models.CharField(max_length=7, default="#42434a", validators=[hex_color_validator])
	hover_clr = models.CharField(max_length=7, default="#e2d6ff", validators=[hex_color_validator])
	text_clr = models.CharField(max_length=7, default="#ffffff", validators=[hex_color_validator])
	accent_clr = models.CharField(max_length=7, default="#6344ab", validators=[hex_color_validator])
	secondary_text_clr = models.CharField(max_length=7, default="#111827", validators=[hex_color_validator])
	container_background_base = models.CharField(max_length=7, default="#ecf4fe", validators=[hex_color_validator])
	secondary_base_clr = models.CharField(max_length=7, default="#60a5fa", validators=[hex_color_validator])
	sidebar_gradient_start = models.CharField(max_length=7, default="#8b5cf6", validators=[hex_color_validator])
	sidebar_gradient_end = models.CharField(max_length=7, default="#60a5fa", validators=[hex_color_validator])

	profile_icon_emoji = models.CharField(max_length=16, blank=True)
	agenda_icon_emoji = models.CharField(max_length=16, blank=True)
	default_activity_icon_emoji = models.CharField(max_length=16, blank=True)

	profile_icon_image = models.ImageField(upload_to="ui_icons/profile/", blank=True, null=True)
	agenda_icon_image = models.ImageField(upload_to="ui_icons/agenda/", blank=True, null=True)
	default_activity_icon_image = models.ImageField(upload_to="ui_icons/activity_default/", blank=True, null=True)

	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Preferências de {self.user}"
