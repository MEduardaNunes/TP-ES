from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

color_validator = RegexValidator(
    regex=r'^#[0-9A-Fa-f]{6}$',
    message='A cor deve ser um código hexadecimal válido (ex: #FF0000).',
    code='invalid_color'
)

DEFAULT_ACTIVITY_TYPE_COLORS = {
    "class": "#3b82f6",
    "exam": "#ef4444",
    "assignment": "#f59e0b",
    "study": "#7c3aed",
    "meeting": "#06b6d4",
    "presentation": "#4f46e5",
    "personal": "#14b8a6",
}


def default_activity_type_colors():
    return DEFAULT_ACTIVITY_TYPE_COLORS.copy()

class Schedule(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#59e7ec", validators=[color_validator])
    icon_emoji = models.CharField(max_length=16, blank=True)
    icon_image = models.ImageField(upload_to="schedule_icons/", blank=True, null=True)
    # Mapping of activity_type -> hex color (e.g. {"exam": "#ef4444", "assignment": "#f59e0b"})
    activity_type_colors = models.JSONField(blank=True, default=default_activity_type_colors)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Participant(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        MEMBER = "member", "Participante"

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name="participants"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="participations"
    )
    
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("schedule", "user")

    def __str__(self):
        return f"{self.user} — {self.schedule} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
class Activity(models.Model):
    class Kind(models.TextChoices):
        EVENT = "event", "Evento"   # tem horário, acontece em um momento
        TASK = "task",  "Tarefa"   # tem prazo, pode ser concluída

    class Priority(models.TextChoices):
        URGENT_IMPORTANT = "urgent_important", "Urgente e importante"
        URGENT = "urgent", "Urgente"
        IMPORTANT = "important", "Importante"
        NOT_URGENT_NOT_IMPORTANT = "not_urgent_not_important", "Não urgente e nem importante"
        
    class Type(models.TextChoices):
        CLASS = "class", "Aula"
        EXAM = "exam", "Prova"
        ASSIGNMENT = "assignment", "Trabalho"
        STUDY = "study", "Estudo"
        
        MEETING = "meeting", "Reunião"
        PRESENTATION = "presentation", "Apresentação"
        
        PERSONAL = "personal", "Pessoal"

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name="activities"
    )
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    activity_type = models.CharField(max_length=20, choices=Type.choices)
    priority = models.CharField(
        max_length=40,
        choices=Priority.choices,
        default=Priority.IMPORTANT,
    )
    date = models.DateField(null=True, blank=True) # opcional para tarefas
    start_time = models.TimeField(null=True, blank=True)  # eventos
    end_time = models.TimeField(null=True, blank=True) # eventos
    notes = models.TextField(blank=True)
    color = models.CharField(max_length=7, blank=True, validators=[color_validator])
    icon_emoji = models.CharField(max_length=16, blank=True)
    icon_image = models.ImageField(upload_to="activity_icons/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if self.kind == self.Kind.EVENT and not self.date:
            raise ValidationError("Eventos devem ter uma data obrigatória.")
    
    def __str__(self):
        date_str = f" ({self.date})" if self.date else ""
        return f"{self.title} — {self.get_activity_type_display()}{date_str}"

    @property
    def is_task(self):
        return self.kind == self.Kind.TASK

    @property
    def is_event(self):
        return self.kind == self.Kind.EVENT
    
class ActivityCheck(models.Model):
    """Marca uma tarefa como concluída por um usuário específico."""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="checks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="checks")
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("activity", "user")

    def __str__(self):
        return f"{self.user} ✔ {self.activity}"
