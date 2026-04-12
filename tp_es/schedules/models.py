from django.db import models
from django.conf import settings

class Schedule(models.Models):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7, default="#6366f1")
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

    def is_admin(self):
        return self.role == self.Role.ADMIN
    
class Event(models.Model):
    class Type(models.TextChoices):
        CLASS = "class", "Aula"
        EXAM = "exam", "Prova"
        ASSIGNMENT = "assignment", "Trabalho"
        STUDY = "study", "Estudo"
        
        MEETING = "meeting", "Reunião"
        TASK = "task", "Tarefa" 
        PRESENTATION = "presentation", "Apresentação"
        
        PERSONAL = "personal", "Pessoal"

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name="events"
    )
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    color = models.CharField(max_length=7, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.get_type_display()} ({self.date})"