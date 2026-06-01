from django.db import models
from lineas_ahorro_app.models import LINEAS_AHORRO
# Create your models here.
class RET_FUE_AHO(models.Model):
    lin_aho = models.ForeignKey(LINEAS_AHORRO, on_delete=models.PROTECT, verbose_name='Línea Ahorro')
    fecha_inicial = models.DateField(null=True, blank=True, verbose_name='Fecha Inicial')
    fecha_final = models.DateField(null=True, blank=True, verbose_name='Fecha Final')
    bas_liq_int = models.FloatField(null=True, blank=True, verbose_name='Base Liquidación Intereses')
    tas_liq_rf = models.FloatField(null=True, blank=True, verbose_name='Tasa Liquidación Retefuente')

    class Meta:
        unique_together = [['lin_aho', 'fecha_inicial']]
        db_table = 'RET_FUE_AHO'

    def __str__(self):
        return self.lin_aho