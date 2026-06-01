from django.db import models
from oficinas_app.models import OFICINAS
from asociados_app.models import ASOCIADOS
from terceros_app.models import TERCEROS
from lineas_credito_app.models import LINEAS_CREDITO
from hecho_economico_app.models import HECHO_ECONO
from contabilizacion_capital_creditos_app.models import IMP_CON_CRE
from justo_app.opciones import OPC_CRE_TERMINO, OPC_CRE_FOR_PAG, OPC_BOOL, OPC_EST_CRE, OPC_CRE_EST_JUR, OPC_CRE_CATEGORIA
from justo_app.opciones import OPC_GARANTIA,OPC_CAMBIOS_CRE,OPC_PRIMA_CREDITO
from datetime import date

# Create your models here.
class CREDITOS(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT,verbose_name='Oficina')
    imputacion = models.ForeignKey(IMP_CON_CRE, on_delete=models.PROTECT, null=True,default=None,verbose_name='Imputacion Contable')
    cod_lin_cre = models.ForeignKey(LINEAS_CREDITO, on_delete=models.PROTECT,null=True,default=None, verbose_name='Línea de Crédito')
    socio = models.ForeignKey(ASOCIADOS, on_delete=models.PROTECT,null=True,default=None,verbose_name='Asociado')
    com_des = models.ForeignKey(HECHO_ECONO,on_delete=models.PROTECT,null=True,default=None,verbose_name='Comprobante Desembolso')
    cod_cre = models.CharField(max_length=10,null=True,verbose_name='Código Crédito')
    cod_des = models.CharField(max_length=1,default=' ',verbose_name='Destino Cre')
    libranza = models.CharField(max_length=10,null=True,blank=True,default='',verbose_name='Libranza')
    pagare = models.CharField(max_length=16,null=True,blank=True,default='',verbose_name='Pagaré')
    termino = models.CharField(max_length=1, choices=OPC_CRE_TERMINO,default='D',verbose_name='Término')
    for_pag = models.CharField(max_length=1, choices=OPC_CRE_FOR_PAG,default='P',verbose_name='Forma de Pago')
    tip_gar = models.CharField(max_length=2, choices=OPC_GARANTIA, default='15', verbose_name='Tipo de Garantía')
    cap_ini = models.FloatField(null=True, blank=True,default=0,verbose_name='Capital Inicial')
    fec_des = models.DateField(null=True, blank=True,verbose_name='Fecha Desembolso')
    fec_pag_ini = models.DateField(null=True, blank=True,verbose_name='Fecha Pago Inicial')
    fec_ree = models.DateField(null=True, blank=True,verbose_name='Fecha Reestructuración')
    fec_ven = models.DateField(null=True, blank=True,verbose_name='Fecha de Vencimiento')
    fec_ult_pag = models.DateField(null=True, blank=True,verbose_name='Fecha Último Pago')
    val_cuo_ini = models.FloatField(null=True, blank=True,verbose_name='Valor Cuota Incial')
    val_cuo_act = models.FloatField(null=True, blank=True,verbose_name='Valor Cuota Actual')
    num_cuo_ini = models.IntegerField(null=True, blank=True,default=0,verbose_name='Número Cuotas Pactadas')
    num_cuo_act = models.IntegerField(null=True, blank=True,default=0,verbose_name='Número Cuotas Actuales')
    num_cuo_gra = models.IntegerField(null=True, blank=True,default=0,verbose_name='Número Cuotas de Gracia')
    per_ano = models.IntegerField(null=True, blank=True,default=12,verbose_name='Periodosa al Año')
    tiae_ic_ini = models.FloatField(null=True, blank=True,default=0.0,verbose_name='Tasa Efectiva Anual')
    tiae_ic_act = models.FloatField(null=True, blank=True,default=0.0,verbose_name='Tasa Efectiva Anual')
    tian_ic_ini = models.FloatField(null=True, blank=True,default=0.0,verbose_name='Tasa Int Cte Mensual Pactado')
    tian_ic_act = models.FloatField(null=True, blank=True,default=0.0,verbose_name='Tasa Int Cte Mensual Actual')
    tian_im = models.FloatField(null=True, blank=True,default=0.0,verbose_name='Tasa Interés Moratorio')
    tian_pol_seg = models.FloatField(null=True, blank=True,default=0.0,verbose_name='Tasa Interés Póliza')
    por_des_pro_pag = models.FloatField(null=True, blank=True,default=0.0,verbose_name='Descuento Pronto Pago')
    decreciente = models.CharField(max_length=1, choices=OPC_BOOL,default='N',verbose_name='Crédito Decreciente?')
    estado = models.CharField(max_length=1,choices=OPC_EST_CRE,default='X',verbose_name='Estado')
    est_jur = models.CharField(max_length=1, choices=OPC_CRE_EST_JUR,default='N',verbose_name='Estado Jurídico')
    cat_nue = models.CharField(max_length=1, choices=OPC_CRE_CATEGORIA,default='A',verbose_name='Categoria Incial')
    rep_cen_rie = models.CharField(max_length=1, choices=OPC_BOOL,default='S',verbose_name='Reportar a Centrales de Riesgos?')
    val_gar_hip = models.FloatField(null=True, blank=True,verbose_name='Valor Garantía Hipotecaria')
    mat_inm_gar = models.CharField(max_length=12, null=True,blank=True,default='',verbose_name='Número Matrícula Inmobiliaria')
    num_pol_gar_hip = models.CharField(max_length=16,blank=True ,null=True,verbose_name='Número Garantia Hipotecaria')
    figarantias = models.CharField(max_length=1, choices=OPC_BOOL,default='N',verbose_name='Figarantías?')
    prima = models.CharField(max_length=2, choices=OPC_PRIMA_CREDITO,default='NO',verbose_name='Primas?')
    porcentaje_prima = models.FloatField(null=True, blank=True,default=0.0,verbose_name='Porcentaje Prima')

    class Meta:
        unique_together = [['oficina', 'cod_cre']]
        indexes = [
            models.Index(fields=['oficina', 'cod_cre']),
            models.Index(fields=['oficina', 'socio'])  
        ]
        db_table = 'creditos'

    def __str__(self):
        return '__all__'

class CODEUDORES(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT)
    credito = models.ForeignKey(CREDITOS, on_delete=models.PROTECT)
    tercero = models.ForeignKey(TERCEROS, on_delete=models.PROTECT)

    class Meta:
        unique_together = [['oficina', 'credito', 'tercero']]
        db_table = 'codeudores'
    
    def __str__(self):
        return f'{self.tercero.doc_ide} - {self.tercero.nombre}' 

class GAR_NO_IDONEA(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT)
    credito = models.ForeignKey(CREDITOS, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=1, null=False, default='C')
    doc_ide = models.CharField(max_length=12, null=False, default='')

    class Meta:
        unique_together = [['oficina', 'credito', 'doc_ide']]
        db_table = 'gar_no_idonea'


