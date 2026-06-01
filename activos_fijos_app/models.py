from django.db import models
from oficinas_app.models import OFICINAS
from detalle_economico_app.models import DETALLE_ECONO
from justo_app.opciones import OPC_BOOL

# Create your models here.
class ACTIVOS_FIJOS(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.CASCADE, verbose_name='Oficina')
    codigo = models.CharField(max_length=8,verbose_name='Codigo del Elemento')
    descripcion = models.CharField(max_length=128,verbose_name='Descripcion del Elemento')
    fecha_de_alta = models.DateField(null=True, blank=False,verbose_name = 'Fecha de alta del Elemento')
    deta_eco = models.ForeignKey(DETALLE_ECONO,null=True, blank=True,on_delete=models.CASCADE, verbose_name='Asiento de Alta')
    valor_elem = models.FloatField(null=True)  
    meses_dep = models.IntegerField(null=True)
    valor_salva = models.FloatField(null=True) 
    dep_acu_vig_ant = models.FloatField(null=True)
    det_acu_vig_ant = models.FloatField(null=True)
    val_acu_vig_ant = models.FloatField(null=True)
    cod_cta_dep = models.CharField(max_length=10, null=True,verbose_name='Cuenta Depreciación')
    cod_cta_dep_gas = models.CharField(max_length=10, null=True,verbose_name='Cta Dep Gasto')
    cod_cta_det = models.CharField(max_length=10, null=True,verbose_name='Cta Deterioro')
    cod_cta_det_gas = models.CharField(max_length=10, null=True,verbose_name='Cta Deterioro Gasto')
    de_baja = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Está de Baja?')

    class Meta:
        unique_together = [['oficina','codigo']]
        indexes = [
            models.Index(fields=['oficina', 'descripcion']),
        ]
        db_table = 'activos_fijos'

    def __str__(self):
        return self.codigo+' '+self.descripcion