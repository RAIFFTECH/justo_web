from django.db import models
from ctas_ahorros_app.models import CTAS_AHORRO
from justo_app.opciones import OPC_EST_CTA_AHO
# Create your models here.
class CTA_AHO_EST_HIS(models.Model):
    cta_aho = models.ForeignKey(CTAS_AHORRO, on_delete=models.PROTECT)
    fecha = models.DateField(null=True, blank=True)
    est_cta_ant = models.CharField(max_length=1, choices=OPC_EST_CTA_AHO)

    class Meta:
        unique_together = [['cta_aho', 'fecha']]
        db_table = 'cta_aho_est_his'

    def __str__(self):
        return self.cta_aho
