from django.db import models
from clientes_app.models import CLIENTES
from justo_app.opciones import OPC_CRE_CATEGORIA
# Create your models here.
class IMP_CON_CRE_INT(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    cod_imp = models.CharField(max_length=2, null=True, verbose_name='Código')
    categoria = models.CharField(max_length=1, choices=OPC_CRE_CATEGORIA, verbose_name='Categoria')
    kcta_con = models.CharField(max_length=10, null=True, verbose_name='Cuenta Contable')
    kcta_pro_ind = models.CharField(max_length=10, null=True, verbose_name='Cuenta Provisión Individual')
    cta_pro_ind_cap = models.CharField(max_length=10, null=True, verbose_name='Cuenta Provisión Ind Kapital')
    cta_pro_ind_int = models.CharField(max_length=10, null=True, verbose_name='Cuenta Provisión Ind Interes')
    kporcentaje = models.FloatField(null=True, blank=True, verbose_name='Porcentaje')
    cta_int = models.CharField(max_length=10, null=True, verbose_name='Cuenta Intereses')
    cta_ord_int = models.CharField(max_length=10, null=True, verbose_name='Cuenta de Orden Intereses')

    class Meta:
        unique_together = [['cliente', 'cod_imp', 'categoria']]
        db_table = 'imp_con_cre_int'

    def __str__(self):
        return self.cliente+' '+self.categoria