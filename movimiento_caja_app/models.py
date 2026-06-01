from django.db import models
from oficinas_app.models import OFICINAS
from cajeros_app.models import CAJEROS
from justo_app.opciones import OPC_BOOL
from django.contrib.auth.models import User

# Create your models here.

class MOV_CAJA(models.Model):
    cajero = models.ForeignKey(CAJEROS, on_delete=models.PROTECT, null=True, verbose_name='Cajero')
    fecha = models.DateField(null=True, blank=True, verbose_name='Fecha')
    jornada = models.CharField(max_length=1, null=False, verbose_name='Jornada')
    saldo_ini = models.FloatField(null=True, blank=True, verbose_name='Saldo Inicial')
    debitos = models.FloatField(null=True, blank=True, verbose_name='Movimientos Débitos')
    creditos = models.FloatField(null=True, blank=True, verbose_name='Movimientos Créditos')
    val_che_dev = models.FloatField(null=True, blank=True, verbose_name='Valor Cheques Devueltos')
    saldo_fin = models.FloatField(null=True, blank=True, verbose_name='Saldo Final')
    diferencia = models.FloatField(null=True, blank=True, verbose_name='Diferencia')
    val_cheques = models.FloatField(null=True, blank=True, verbose_name='Valor Cheques')
    val_vales = models.FloatField(null=True, blank=True, verbose_name='Valor Vales')
    cerrado = models.CharField(max_length=1, null=False, choices=OPC_BOOL, verbose_name='Cierre de Caja?')
    monedas = models.JSONField(null=True, blank=True, verbose_name='Dinero en Efectivo')
    class Meta:
        unique_together = [['cajero','fecha', 'jornada']]
        db_table = 'mov_caja'

    def __str__(self) -> str:
        return self.cajero+' '+self.fecha+' '+self.jornada