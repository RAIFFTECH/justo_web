from django.db import models
from clientes_app.models import CLIENTES
# Create your models here.
class LINEAS_CREDITO(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    cod_lin_cre = models.IntegerField(verbose_name='Código')
    descripcion = models.CharField(max_length=44,null = True, verbose_name='Descripción')
    tas_int_anu = models.FloatField(null = True, verbose_name='Tasa Interés Anual')
    tas_int_mor = models.FloatField(null = True, verbose_name='Tasa Interés Mora')
    por_pol = models.FloatField(null = True, verbose_name='Porcentaje Póliza')
    por_des_pp = models.FloatField(null = True, verbose_name='Descuento Pronto Pago')
    dia_con_int_mor = models.IntegerField(null = True, verbose_name='Días Condonación Interés Mora')
    class Meta:
        unique_together = [['cliente','cod_lin_cre']]
        db_table = 'lineas_credito'

    def __str__(self):
        cod_lin_cre = str(self.cod_lin_cre) if self.cod_lin_cre is not None else ''
        descripcion = str(self.descripcion) if self.descripcion is not None else ''
        return f'{cod_lin_cre} - {descripcion}'
