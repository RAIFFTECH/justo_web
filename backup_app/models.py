from django.db import models
from django.utils import timezone

class Backup(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    filename = models.CharField(max_length=100)
    usuario = models.CharField(max_length=30)

    class Meta:
        unique_together = [['timestamp']]
        db_table = 'backup'

    def __str__(self):
        return self.usuario+' '+self.filename

