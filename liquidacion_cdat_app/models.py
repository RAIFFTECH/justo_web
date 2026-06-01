from django.db import models
from justo_app.opciones import OPC_BOOL, OPC_LIQ_INT_AHO
from ctas_ahorros_app.models import CTAS_AHORRO, OPC_BOOL
from ampliacion_cdat_app.models import CTA_CDAT_AMP
from hecho_economico_app.models import HECHO_ECONO
# Create your models here.

class CTA_CDAT_LIQ(models.Model):
    cta_aho = models.ForeignKey(CTAS_AHORRO, on_delete=models.PROTECT, verbose_name='Cuenta de Ahorro')
    cta_amp = models.ForeignKey(CTA_CDAT_AMP, on_delete=models.PROTECT, verbose_name='Cuenta Ampliación')
    fecha = models.DateField(null=True, blank=True, verbose_name='Fecha')
    tip_liq = models.CharField(max_length=1, choices=OPC_LIQ_INT_AHO, verbose_name='Tipo Liquidación')
    val_int = models.FloatField(null=True, blank=True, verbose_name='Valor Intereses')
    val_ret = models.FloatField(null=True, blank=True, verbose_name='Valor Retefuente')
    val_ret_nue = models.FloatField(null=True, blank=True, verbose_name='Valor Retefuente Nueva')
    aplicado = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Aplicado?')
    docto = models.ForeignKey(HECHO_ECONO, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Número Documento')

    class Meta:
        unique_together = [['cta_aho', 'cta_amp', 'fecha', 'tip_liq']]
        db_table = 'cta_cdat_liq'

    def __str__(self):
        return self.cta_aho