import django.core.validators
from django.db import migrations, models


OLD_DEFAULT = "#6366f1"
NEW_DEFAULT = "#59e7ec"


def forward_update_default_color(apps, schema_editor):
    Schedule = apps.get_model("schedules", "Schedule")
    Schedule.objects.filter(color=OLD_DEFAULT).update(color=NEW_DEFAULT)


def backward_update_default_color(apps, schema_editor):
    Schedule = apps.get_model("schedules", "Schedule")
    Schedule.objects.filter(color=NEW_DEFAULT).update(color=OLD_DEFAULT)


class Migration(migrations.Migration):

    dependencies = [
        ("schedules", "0004_activity_icon_emoji_activity_icon_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schedule",
            name="color",
            field=models.CharField(
                default="#59e7ec",
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
        migrations.RunPython(forward_update_default_color, backward_update_default_color),
    ]
