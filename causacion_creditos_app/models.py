from django.db import models
from oficinas_app.models import OFICINAS
from hecho_economico_app.models import HECHO_ECONO
# Create your models here.

class CREDITOS_CAUSA(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT, default=None, verbose_name='Oficina')
    cod_cre = models.CharField(max_length=10, null=True, verbose_name='Código Crédito')
    comprobante = models.ForeignKey(HECHO_ECONO, on_delete=models.PROTECT, null=True, default=None, verbose_name='Comprobante')
    cuota = models.IntegerField(null=False, blank=False, default=0, verbose_name='Cuota')
    fecha = models.DateField(null=True, blank=True, verbose_name='Fecha')
    capital = models.FloatField(null=True, blank=True, verbose_name='Capital')
    int_cor = models.FloatField(null=True, blank=True, verbose_name='Interés Corriente')

    class Meta:
        unique_together = [['oficina', 'cod_cre', 'comprobante', 'cuota']]
        db_table = 'creditos_causa'
        indexes = [
            models.Index(fields=['oficina', 'cod_cre', 'comprobante']),
        ]

    def __str__(self) -> str:
        return str(self.oficina)+' '+self.cod_cre
