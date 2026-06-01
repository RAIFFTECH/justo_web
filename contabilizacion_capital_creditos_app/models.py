from django.db import models
from clientes_app.models import CLIENTES
# Create your models here.

#class MODALIDAD(models.Model):
#    cod_mod = models.CharField(max_length=1, null=True, verbose_name='Código')


class MODALIDADES(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    cod_mod = models.CharField(max_length=1, null=True, verbose_name='Código') 
    num_rango = models.IntegerField(null=True, blank=True,default=0,verbose_name='Num Rango')
    cod_cta =  models.CharField(max_length=10, null=True, verbose_name='Cuenta de Orden')
    max_dias = models.IntegerField(null=True, blank=True,default=0,verbose_name='Num Rango')
    class Meta:
        unique_together = [['cliente', 'cod_mod','num_rango']]
        db_table = 'modalidades'

class IMP_CON_CRE(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    cod_imp = models.CharField(max_length=2, null=True, verbose_name='Código')
    cod_mod = models.CharField(max_length=1, null=True, verbose_name='Código') 
    descripcion = models.CharField(max_length=40, null=True, verbose_name='Descripción')
    kpte_cap = models.CharField(max_length=10, null=True, verbose_name='Cuenta Puente Capital')
    kdet_gen_adi = models.CharField(max_length=10, null=True, verbose_name='Provisión General Adicional')
    kdet_gen = models.CharField(max_length=10, null=True, verbose_name='Provisión General')
    kdet_gen_gas = models.CharField(max_length=10, null=True, verbose_name='Cuenta Gasto Provisión')
    kdet_gen_rec = models.CharField(max_length=10, null=True, verbose_name='Cuenta Provisión Recuperada')
    kdet_ind_gas= models.CharField(max_length=10, null=True, verbose_name='Cuenta Provisión Individual Gasto')
    kdet_ind_rec = models.CharField(max_length=10, null=True, verbose_name='Cuenta Provisión Individual Recuperada')
    kdpp_ic = models.CharField(max_length=10, null=True, verbose_name='Cuenta Descuento Pronto Pago IC' )
    kpte_ic = models.CharField(max_length=10, null=True, verbose_name='Cuenta Puente IC')
    cta_val = models.CharField(max_length=10, null=True, verbose_name='Cuenta Valorización')
    kcta_ingreso = models.CharField(max_length=10, null=True, verbose_name='Cuenta Ingresos')
    kic_orden_i = models.CharField(max_length=10, null=True, verbose_name='Cuenta de Orden IC')
    kic_cxp = models.CharField(max_length=10, null=True, verbose_name='Cuenta por Pagar')
    kic_rec_int = models.CharField(max_length=10, null=True, verbose_name='Cuenta por Pagar')
    

    class Meta:
        unique_together = [['cliente', 'cod_imp']]
        db_table = 'imp_con_cre'

    
    def __str__(self):
        cod_imp = str(self.cod_imp) if self.cod_imp is not None else ''
        descripcion = str(self.descripcion) if self.descripcion is not None else ''
        return f'{cod_imp} - {descripcion}'
