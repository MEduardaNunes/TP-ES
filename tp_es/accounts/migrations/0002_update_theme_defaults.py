import django.core.validators
from django.db import migrations, models


OLD_VALUES = {
    "container_background_base": "#f3f0fe",
    "secondary_base_clr": "#ce9aff",
    "sidebar_gradient_start": "#8b5cf6",
    "sidebar_gradient_end": "#60a5fa",
}

NEW_VALUES = {
    "container_background_base": "#ecfeff",
    "secondary_base_clr": "#67e8f9",
    "sidebar_gradient_start": "#0ea5e9",
    "sidebar_gradient_end": "#22d3ee",
}


def forward_update_defaults(apps, schema_editor):
    UserThemePreference = apps.get_model("accounts", "UserThemePreference")
    for field, old_value in OLD_VALUES.items():
        UserThemePreference.objects.filter(**{field: old_value}).update(**{field: NEW_VALUES[field]})


def backward_update_defaults(apps, schema_editor):
    UserThemePreference = apps.get_model("accounts", "UserThemePreference")
    for field, new_value in NEW_VALUES.items():
        UserThemePreference.objects.filter(**{field: new_value}).update(**{field: OLD_VALUES[field]})


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userthemepreference",
            name="container_background_base",
            field=models.CharField(
                default="#ecfeff",
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
                default="#67e8f9",
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
                default="#0ea5e9",
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
                default="#22d3ee",
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
        migrations.RunPython(forward_update_defaults, backward_update_defaults),
    ]
