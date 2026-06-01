from django.db import models
from clientes_app.models import CLIENTES
from justo_app.opciones import OPC_BOOL, OPC_NAT,OPC_TIP_CTA
# Create your models here.

class PLAN_CTAS(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT,verbose_name='Cliente')
    per_con = models.IntegerField(blank=True, null=True,verbose_name='Periodo Contable')
    cod_cta = models.CharField(max_length=10, null=True,verbose_name='Código Cuenta')
    nom_cta = models.CharField(max_length=64, null=True,verbose_name='Nombre Cuenta')
    tip_cta = models.CharField(max_length=1, choices=OPC_TIP_CTA,null=True,verbose_name='Tipo Cuenta')
    dinamica = models.TextField(blank=True,verbose_name='Dinámica')
    naturaleza = models.CharField(max_length=1, choices=OPC_NAT,verbose_name='Naturaleza')
    activa = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta Activa?')
    por_tercero = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Contabiliza por Tercero?')
    cta_act_fij = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta Activo Fijo?')
    cta_pre = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta Presupuesto?')
    cta_bal = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta de Balance?')
    cta_res = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta de Resultados?')
    cta_ord = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta de Orden?')
    cta_ban = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta de Banco?')
    cta_gan_per = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Cuenta Ganancias?')
    cta_per_gan = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta Pérdidas?')
    cta_dep = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta Depreciación?')
    cta_ing_ret = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Cuenta Ingresos y Retenciones?')
    cta_ret_iva = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta Reteiva?')
    cta_rec = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Cuenta Recíproca?')
    id_ds = models.BigIntegerField(null=True,blank=True, db_index=True)

    class Meta:
        unique_together = [['cliente', 'per_con', 'cod_cta']]
        db_table = 'plan_ctas'

    def __str__(self):
        return self.cod_cta+'-' + self.nom_cta
