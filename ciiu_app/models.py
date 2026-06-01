from django.db import models
from clientes_app.models import CLIENTES

class CIIU(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    codigo = models.CharField(max_length=5, blank=False, null=False, verbose_name='Código')
    actividad = models.CharField(max_length=256, blank=False, null=False, verbose_name='Actividad')
   
    class Meta:
        unique_together = [['cliente', 'codigo']]
        db_table = 'ciiu'

    def __str__(self):
        return self.codigo + ' ' +self.actividad
