from django.db import models
from oficinas_app.models import OFICINAS
from terceros_app.models import TERCEROS
from conceptos_app.models import CONCEPTOS
from hecho_economico_app.models import HECHO_ECONO
from justo_app.opciones import OPC_BOOL,OPC_EST_CRE


# Create your models here.
class CTAS_X_COBRAR(models.Model):
    id = models.BigAutoField(primary_key=True)
    oficina =  models.ForeignKey(OFICINAS, on_delete=models.CASCADE)
    cod_cxc =  models.CharField(max_length=10,null = False)
    tercero = models.ForeignKey(TERCEROS, on_delete=models.CASCADE, null=True, blank=True)  # 🔹 Permite nulos
    concepto = models.ForeignKey(CONCEPTOS, on_delete=models.CASCADE, null=True, blank=True)
    valor = models.FloatField(null = True)
    fecha_des = models.DateField(null=True,blank=True)
    fecha_exi = models.DateField(null=True,blank=True)
    aplicado = models.CharField(max_length=1, choices=OPC_EST_CRE)
    class Meta:
        unique_together = [['oficina','cod_cxc']]
        db_table = 'ctas_x_cobrar'
        indexes = [
            models.Index(fields=['oficina', 'concepto']),  # Ya exist
            models.Index(fields=['oficina', 'tercero']),  # Ya exist
        ]
        
class CXC_DET(models.Model):
    id = models.BigAutoField(primary_key=True)
    cuenta_x_cobrar =  models.ForeignKey(CTAS_X_COBRAR, on_delete=models.CASCADE)
    hecho_econo = models.ForeignKey(HECHO_ECONO, on_delete=models.CASCADE,null=True,blank=True)
    fecha = models.DateField(null=True,blank=True)
    tip_mov = models.CharField(max_length=1)
    valor = models.FloatField(null = True)
    class Meta:
        unique_together = [['cuenta_x_cobrar','fecha']]
        db_table = 'cxc_det'

