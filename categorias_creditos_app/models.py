from django.db import models
from clientes_app.models import CLIENTES
from justo_app.opciones import OPC_CRE_CATEGORIA
# Create your models here.
class CAT_DES_DIA_CRE(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    codigo = models.IntegerField(verbose_name='Código')
    categoria = models.CharField(max_length=1, null=False, choices=OPC_CRE_CATEGORIA, verbose_name='Categoria')
    minimo_dias = models.IntegerField(null=True, verbose_name='Mínimo Días')
    maximo_dias = models.IntegerField(null=True, verbose_name='Máximo Días')

    class Meta:
        unique_together = [['cliente', 'codigo', 'categoria']]
        db_table = 'cat_des_dia_cre'

    def __str__(self) -> str:
        return self.cliente+' '+self.categoria
