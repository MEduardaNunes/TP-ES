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