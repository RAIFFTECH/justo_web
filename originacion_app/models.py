from django.db import models
from asociados_app.models import ASOCIADOS
from justo_app.opciones import OPC_BOOL,OPC_CRE_FOR_PAG


# Create your models here.
class ORIGINACION(models.Model):
    # fec_inf = models.DateField(null=True, blank=True, verbose_name='Fecha Información')
    # tipo_asesoria =  models.CharField(max_length=1, blank=True, null=True, choices=OPC_ASESORIA, default='1', verbose_name='Tipo Asesoría')
    # tercero = models.ForeignKey(TERCEROS, on_delete=models.PROTECT, verbose_name='Tercero')
    asociado = models.ForeignKey(ASOCIADOS, on_delete=models.PROTECT, verbose_name='Asociado')
    lin_cre = models.CharField(max_length=80, null=False, verbose_name='Línea de Crédito')
    monto = models.FloatField(blank=True, null=True, verbose_name='Monto')
    plazo = models.IntegerField(blank=True, null=True, verbose_name='Plazo')
    gar_cre_sol = models.CharField(max_length=1, null=False, verbose_name='Garantía Crédito Solidario?')
    lin_cre_sol = models.CharField(max_length=1, null=False, verbose_name='Línea Crédito Solidario')
    mod_cre_sol = models.CharField(max_length=1, null=False, verbose_name='Modalidad Crédito Solidario')
    sol_cre_edu = models.CharField(max_length=1, null=False,choices=OPC_BOOL,default='N', verbose_name='Solicitud de credito')
    for_pag = models.CharField(max_length=1, null=False,choices=OPC_CRE_FOR_PAG,default='P', verbose_name='Forma de pago')

    class Meta:
        unique_together = [['asociado']]
        db_table = 'originacion'

    def __str__(self):
        return self.asociado
