from django.db import models
from clientes_app.models import CLIENTES
from justo_app.opciones import OPC_BOOL,OPC_EST_CRE
from oficinas_app.models import OFICINAS
from terceros_app.models import TERCEROS


class CONCEPTOS(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, null=True, verbose_name='Cliente')
    cod_con = models.CharField(max_length=8, null=False, verbose_name='Código Concepto')
    con_justo = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Concepto Justo')
    descripcion = models.CharField(max_length=44, null=False, verbose_name='Descripción')
    tip_dev_ap = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Tipo Devolución Aportes')
    tip_con = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Tipo Concepto')
    tip_sis = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Tipo Sistema')
    cta_con = models.CharField(max_length=10, blank=True, null=False, verbose_name='Cuenta Contable')
    cta_con_pas = models.CharField(max_length=10, blank=True, null=False, verbose_name='Cuenta Contable Pasivo')
    debito = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Concepto Débito?')
    credito = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Concepto Crédito?')
    por_tercero = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Usa Tercero?')
    por_ret_fue = models.FloatField(null=True, blank=True, verbose_name='% Retefuente?')

    class Meta:
        unique_together = [['cliente', 'cod_con']]
        db_table = 'conceptos'

    def __str__(self):
        return self.cod_con
    


