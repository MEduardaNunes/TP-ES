import django.core.validators
from django.db import migrations, models


CYAN_VALUES = {
    "container_background_base": "#ecfeff",
    "secondary_base_clr": "#67e8f9",
    "sidebar_gradient_start": "#0ea5e9",
    "sidebar_gradient_end": "#22d3ee",
}

ORIGINAL_VALUES = {
    "container_background_base": "#f3f0fe",
    "secondary_base_clr": "#ce9aff",
    "sidebar_gradient_start": "#8b5cf6",
    "sidebar_gradient_end": "#60a5fa",
}


def forward_restore_defaults(apps, schema_editor):
    UserThemePreference = apps.get_model("accounts", "UserThemePreference")
    for field, cyan_value in CYAN_VALUES.items():
        UserThemePreference.objects.filter(**{field: cyan_value}).update(**{field: ORIGINAL_VALUES[field]})


def backward_restore_defaults(apps, schema_editor):
    UserThemePreference = apps.get_model("accounts", "UserThemePreference")
    for field, original_value in ORIGINAL_VALUES.items():
        UserThemePreference.objects.filter(**{field: original_value}).update(**{field: CYAN_VALUES[field]})


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_update_theme_defaults"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userthemepreference",
            name="container_background_base",
            field=models.CharField(
                default="#f3f0fe",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        code="invalid_color",
                        message="A cor deve ser um código hexadecimal válido (ex: #FF0000).",
                        regex="^#[0-9A-Fa-f]{6}$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="userthemepreference",
            name="secondary_base_clr",
            field=models.CharField(
                default="#ce9aff",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        code="invalid_color",
                        message="A cor deve ser um código hexadecimal válido (ex: #FF0000).",
                        regex="^#[0-9A-Fa-f]{6}$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="userthemepreference",
            name="sidebar_gradient_start",
            field=models.CharField(
                default="#8b5cf6",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        code="invalid_color",
                        message="A cor deve ser um código hexadecimal válido (ex: #FF0000).",
                        regex="^#[0-9A-Fa-f]{6}$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="userthemepreference",
            name="sidebar_gradient_end",
            field=models.CharField(
                default="#60a5fa",
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        code="invalid_color",
                        message="A cor deve ser um código hexadecimal válido (ex: #FF0000).",
                        regex="^#[0-9A-Fa-f]{6}$",
                    )
                ],
            ),
        ),
        migrations.RunPython(forward_restore_defaults, backward_restore_defaults),
    ]
