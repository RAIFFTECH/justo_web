from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('C', 'Creación'),
        ('M', 'Modificación'),
        ('D', 'Eliminación'),
    ]

    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=255)
    object_id = models.BigIntegerField(null=True)
    changes = models.JSONField(null=True, blank=True)  # Para almacenar los cambios

    class Meta:
        ordering = ['-timestamp']
