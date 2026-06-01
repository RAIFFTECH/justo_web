from django.db import models
from lineas_ahorro_app.models import LINEAS_AHORRO
# Create your models here.

class IMP_CON_LIN_AHO(models.Model):
    linea_ahorro = models.ForeignKey(LINEAS_AHORRO, on_delete=models.PROTECT, null=True, verbose_name='Línea de Ahorro')
    cod_imp = models.CharField(max_length=2, null=True, verbose_name='Código')
    descripcion = models.CharField(max_length=40, null=True, verbose_name='Descripción')
    ctaafeact = models.CharField(max_length=10, null=True, verbose_name='Cuenta Activa')
    ctaafeina = models.CharField(max_length=10, null=True, verbose_name='Cuenta Inactiva')
    ctaafeint = models.CharField(max_length=10, null=True, verbose_name='Cuenta Intereses')
    ctaretfue = models.CharField(max_length=10, null=True, verbose_name='Cuenta Retefuente')

    class Meta:
        unique_together = [['linea_ahorro', 'cod_imp']]
        db_table = 'imp_con_lin_aho'

    def __str__(self):
        return f"{self.linea_ahorro.nombre} - {self.descripcion}"
      
