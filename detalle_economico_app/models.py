from django.db import models
from hecho_economico_app.models import HECHO_ECONO
from detalle_producto_app.models import DETALLE_PROD
from cuentas_app.models import PLAN_CTAS
from terceros_app.models import TERCEROS
# Create your models here.

class DETALLE_ECONO(models.Model):
    hecho_econo = models.ForeignKey(HECHO_ECONO, on_delete=models.PROTECT, verbose_name='Documento')
    detalle_prod = models.ForeignKey(DETALLE_PROD, on_delete=models.PROTECT, null=True, verbose_name='Detalle Producto')
    cuenta = models.ForeignKey(PLAN_CTAS, on_delete=models.PROTECT, verbose_name='Cuenta Contable')
    tercero = models.ForeignKey(TERCEROS, on_delete=models.PROTECT, verbose_name='Tercero')
    item_concepto = models.CharField(max_length=6, null=True, verbose_name='Item Concepto')
    detalle = models.TextField(null=True, verbose_name='Detalle')
    debito = models.FloatField(null=True, verbose_name='Valor Débito',default = 0)
    credito = models.FloatField(null=True, verbose_name='Valor Crédito',default = 0)
    valor_1 = models.FloatField(null=True, verbose_name='Valor 1',default = 0)
    valor_2 = models.FloatField(null=True, verbose_name='Valor 2',default = 0)
    id_ds = models.BigIntegerField(null=True, verbose_name='id_ds',default = 0)

    class Meta:
        #    unique_together = [['hecho_econo','cuenta','tercero','detalle_prod']]
        indexes = [
            models.Index(fields=['hecho_econo', 'cuenta','tercero', 'detalle_prod']),
            models.Index(fields=['item_concepto'])
        ]
        db_table = 'detalle_econo'

    def __str__(self):
        return str(self.hecho_econo.numero)+' '+str(self.detalle_prod.id)