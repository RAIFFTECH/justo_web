from django.db import models
from oficinas_app.models import OFICINAS
from hecho_economico_app.models import HECHO_ECONO
from centrocostos_app.models import CENTROCOSTOS
from justo_app.opciones import OPC_PRODUCTO
# Create your models here.

class DETALLE_PROD(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT, null=True, verbose_name='Oficina')
    hecho_econo = models.ForeignKey(HECHO_ECONO, on_delete=models.PROTECT, verbose_name='Documento',related_name='detalles')
    centro_costo = models.ForeignKey(CENTROCOSTOS, on_delete=models.PROTECT, null=True, verbose_name='Centro de Costo')
    producto = models.CharField(max_length=2, choices=OPC_PRODUCTO, verbose_name='Producto')
    subcuenta = models.CharField(max_length=12, null=True, verbose_name='Subcuenta')
    concepto = models.CharField(max_length=8, null=True, verbose_name='Concepto')
    valor = models.FloatField(null=True, verbose_name='Valor')

    class Meta:
        unique_together = [
            ['hecho_econo', 'producto', 'subcuenta', 'concepto']]
        indexes = [
            models.Index(fields=['oficina', 'producto', 'subcuenta']),  # Índice solo con campos directos
            models.Index(fields=['producto', 'subcuenta', 'hecho_econo'])
        ]
        db_table = 'detalle_prod'

    def __str__(self):
         return f'{self.oficina} {self.hecho_econo.descripcion}'