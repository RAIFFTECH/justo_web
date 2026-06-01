from django.db import models
from lineas_ahorro_app.models import LINEAS_AHORRO
# Create your models here.
class TAS_LIN_AHO(models.Model):
    lin_aho = models.ForeignKey(LINEAS_AHORRO, on_delete=models.PROTECT, verbose_name='Línea de Ahorro')
    fecha_inicial = models.DateField(null=True, blank=True, verbose_name='Fecha Inicial')
    fecha_final = models.DateField(null=True, blank=True, verbose_name='Fecha Final')
    tiae = models.FloatField(verbose_name='Tasa Interés Anual Efectiva')

    class Meta:
        unique_together = [['lin_aho', 'fecha_inicial']]
        db_table = 'tas_lin_aho'
    
    def __str__(self):
        return self.lin_aho
