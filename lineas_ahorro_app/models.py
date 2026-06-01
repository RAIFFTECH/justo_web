from django.db import models
from clientes_app.models import CLIENTES
from justo_app.opciones import OPC_TERMINO, OPC_PER_LIQ_INT
# Create your models here.

class LINEAS_AHORRO(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, null=True,verbose_name='Cliente')
    cod_lin_aho = models.CharField(max_length=2, null=True,verbose_name='Código')
    nombre = models.CharField(max_length=30, null=True,verbose_name='Línea Ahorro')
    termino = models.CharField(max_length=1, choices=OPC_TERMINO,verbose_name='Termino')
    per_liq_int = models.CharField(max_length=1, choices=OPC_PER_LIQ_INT,verbose_name='Periodo Liquidación')
    cta_por_pas = models.CharField(max_length=10, null=True,verbose_name='Cuenta Contable Abono Intereses')
    fec_ult_liq_int = models.DateField(null=True, blank=True,verbose_name='Última Liquidación Intereses')
    saldo_minimo = models.FloatField(null=True, blank=True,verbose_name='Saldo Mínimo')

    class Meta:
        unique_together = [['cliente', 'cod_lin_aho']]
        db_table = 'lineas_ahorro'

    def __str__(self):
        return self.nombre
    


