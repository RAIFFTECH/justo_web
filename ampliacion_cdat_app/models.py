from django.db import models
from ctas_ahorros_app.models import CTAS_AHORRO
from cdat_app.models import CTA_CDAT
from hecho_economico_app.models import HECHO_ECONO
from justo_app.models import OPC_BOOL
# Create your models here.

class CTA_CDAT_AMP(models.Model):
    cta_aho = models.ForeignKey(CTAS_AHORRO, on_delete=models.PROTECT, verbose_name='Cuenta de Ahorro')
    cta_amp = models.ForeignKey(CTA_CDAT, on_delete=models.PROTECT, verbose_name='Cuenta Ampliación')
    fecha = models.DateField(null=True, blank=True, verbose_name='Fecha')
    num_liq = models.IntegerField(null=True, blank=True, verbose_name='Número Liquidación')
    valor = models.FloatField(null=True, blank=True, verbose_name='Valor')
    cta_aho_afe = models.CharField(max_length=10, null=True, verbose_name='Cuenta de Ahorro Afectada')
    docto = models.ForeignKey(HECHO_ECONO, on_delete=models.PROTECT, null=True, blank=True,verbose_name='Número Documento')
    clase = models.CharField(max_length=1, verbose_name='Clase')
    documento = models.CharField(max_length=10, null=True, verbose_name='Documento')
    aplicado = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Aplicado?')

    class Meta:
        unique_together = [['cta_aho', 'cta_amp', 'fecha']]
        db_table = 'cta_cdat_amp'

    def __str__(self):
        return self.cta_aho+' '+self.cta_amp
