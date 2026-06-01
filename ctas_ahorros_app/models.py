from django.db import models
from oficinas_app.models import OFICINAS
from asociados_app.models import ASOCIADOS
from hecho_economico_app.models import HECHO_ECONO
from lineas_ahorro_app.models import LINEAS_AHORRO
from justo_app.opciones import OPC_BOOL,OPC_EST_CTA_AHO,OPC_CANJE

# Create your models here.

class CTAS_AHORRO(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT,verbose_name='Oficina')
    lin_aho = models.ForeignKey(LINEAS_AHORRO, on_delete=models.PROTECT,verbose_name='Línea de Ahorro')
    asociado = models.ForeignKey(ASOCIADOS, on_delete=models.PROTECT,verbose_name='Nombre Asociado')
    num_cta = models.CharField(max_length=10, null=True,verbose_name='Número Cuenta')
    est_cta = models.CharField(max_length=1, choices=OPC_EST_CTA_AHO,verbose_name='Estado Cuenta')
    fec_apertura = models.DateField(null=True, blank=True,verbose_name='Fecha Apertura')
    fec_cancela = models.DateField(null=True, blank=True,verbose_name='Fecha Cancelación')
    exc_tas_mil = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Exenta 4x1000')
    fec_ini_exc = models.DateField(null=True, blank=True,verbose_name='Fecha Exención')
    cod_imp = models.CharField(max_length=2,blank = True,verbose_name='cod_imp')

    class Meta:
        unique_together = [['oficina', 'num_cta']]
        db_table = 'ctas_ahorro'

    def __str__(self):
        return f"{self.num_cta} - {self.est_cta}"

class CANJE_AHORROS(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT,default = None, verbose_name='Oficina')
    cta_aho = models.ForeignKey(CTAS_AHORRO, on_delete=models.PROTECT,verbose_name='Cuenta de Ahorro')
    num_cta = models.CharField(max_length=10,null = True,verbose_name='Número Cuenta')
    hec_eco_1 = models.ForeignKey(HECHO_ECONO,on_delete=models.PROTECT,verbose_name='comprob1',
        related_name='canjes_ahorros_comprob1')
    fecha_1 = models.DateField(null=True, blank=True)
    valor_1 = models.BigIntegerField(null=True)
    estado =  models.CharField(max_length=1,choices=OPC_CANJE,null = True,verbose_name='Estado')
    hec_eco_2 = models.ForeignKey(HECHO_ECONO,on_delete=models.PROTECT,verbose_name='comprob2',
        null=True,blank=True,related_name='canjes_ahorros_comprob2')
    fecha_2 = models.DateField(null=True, blank=True,verbose_name='Fecha Canje2')
    valor_2 = models.BigIntegerField(null=True)
    aplicado = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Aplicado')

    class Meta:
        unique_together = [['oficina','cta_aho','hec_eco_1']]
        db_table = 'canje_ahorros'  

class INT_DIA_AHO(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT,default = None, verbose_name='Oficina')
    cta_aho = models.ForeignKey(CTAS_AHORRO, on_delete=models.PROTECT,verbose_name='Cuenta de Ahorro')
    num_cta = models.CharField(max_length=10,null = True,verbose_name='Número Cuenta')
    dia_mes = models.IntegerField(verbose_name='Día del Mes')
    fecha = models.DateField(null=True,blank=True, verbose_name='Fecha')
    int_dia = models.BigIntegerField(null=True, verbose_name='Interes Diario')
    ret_fue = models.BigIntegerField(null=True, verbose_name='Retefuente')
    aplicado = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Aplicado')
    class Meta:
        unique_together = [['oficina','cta_aho','dia_mes']]
        db_table = 'int_dia_aho'  

class TEMPO_AHO(models.Model):
    num_cta = models.CharField(max_length=10,null = True)
    agno = models.IntegerField()
    mes = models.IntegerField()
    valor =  models.BigIntegerField()
    class Meta:
        unique_together = [['num_cta','agno','mes']]
        db_table = 'tempo_aho'  

class XAJU_SAL_AHO(models.Model):
    agno = models.IntegerField()
    num_cta = models.CharField(max_length=10,null = True)
    est_cta = models.CharField(max_length=1, choices=OPC_EST_CTA_AHO,verbose_name='Estado Cuenta')
    valor =  models.BigIntegerField()
    class Meta:
        unique_together = [['agno','num_cta']]
        db_table = 'xaju_sal_aho'  

class xTempo02(models.Model):
    doc_ide = models.CharField(max_length=12, null=True)
    num_cta = models.CharField(max_length=10, null=True)
    agno = models.IntegerField()
    mes = models.IntegerField()
    valor =  models.FloatField()
    valor_apl = models.FloatField(default = 0)
    
    class Meta:
        unique_together = [['agno', 'mes','doc_ide','num_cta']]
        db_table = 'xTempo02'

