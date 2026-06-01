from django.db import models
from oficinas_app.models import OFICINAS,OPC_BOOL
# Create your models here.
class CIERRE_MES(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT, null=True, verbose_name='Oficina')
    fecha = models.DateField(null=True, blank=True, verbose_name='Fecha')
    protegido = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Protegido?')
    tot_deb = models.FloatField(null = True,blank = True, verbose_name='Total Débito')
    tot_cre = models.FloatField(null = True,blank = True, verbose_name='Total Crédito')
    fec_cie = models.DateTimeField(null = True,blank = True, verbose_name='Fecha de Cierre')
    usuario = models.CharField(max_length=16, null=False, verbose_name='Usuario')
    class Meta:
        unique_together = [['oficina','fecha']]
        db_table = 'cierre_mes'

    def __str__(self):
        return self.oficina+' '+self.fecha