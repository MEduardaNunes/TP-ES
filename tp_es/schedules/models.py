from django.db import models
from django.conf import settings

class Schedule(models.Models):
    class Day(models.TextChoices):
        SEGUNDA = "SEG", "Segunda-feira"
        TERCA = "TER", "Terça-feira"
        QUARTA = "QUA", "Quarta-feira"
        QUINTA = "QUI", "Quinta-feira"
        SEXTA = "SEX", "Sexta-feira"
        SABADO = "SAB", "Sábado"
        DOMINGO = "DOM", "Domingo"
        
    name = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_schedules"
    )
    color = models.CharField(max_length=7, default="#6366f1")
    created_at = models.DateTimeField(auto_now_add=True)
    days_of_week = models.JSONField(default=list)
    
    def __str__(self):
        return self.name
    