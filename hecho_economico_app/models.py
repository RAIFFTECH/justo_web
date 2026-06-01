from django.db import models
from django.contrib.auth.models import User
from documentos_app.models import DOCTO_CONTA, OPC_BOOL
from terceros_app.models import TERCEROS
from cuentas_app.models import PLAN_CTAS
from localidades_app.models import LOCALIDADES
from justo_app.opciones import OPC_CANALES
# Create your models here.

class HECHO_ECONO(models.Model):
    docto_conta = models.ForeignKey(DOCTO_CONTA, on_delete=models.PROTECT, verbose_name='Documento')
    numero = models.IntegerField(blank=True, null=True, verbose_name='Número')
    fecha = models.DateField(null=True, blank=True, verbose_name='Fecha')
    valor = models.FloatField(null=True, blank=True, verbose_name='Valor Comprobante')
    descripcion = models.CharField(max_length=64, null=True, verbose_name='Descripción')
    anulado = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Anulado?')
    protegido = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Protegido?')
    fecha_prot = models.DateTimeField(auto_now=True, verbose_name='Fecha Protegido')
    usuario = models.CharField(max_length=16, null=True,blank = True, verbose_name='Usuario')
    canal = models.CharField(max_length=3, choices=OPC_CANALES, verbose_name='Canal')
    banco = models.ForeignKey(PLAN_CTAS, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Banco')
    cheque = models.CharField(max_length=16, null=True, verbose_name='Cheque')
    beneficiario = models.CharField(max_length=12, null=True, verbose_name='Beneficiario')
    ciudad = models.ForeignKey(LOCALIDADES,on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    id_ds = models.BigIntegerField(null=True, db_index=True, verbose_name='id_ds')
    class Meta:
        unique_together = [['docto_conta', 'numero']]
        indexes = [
            models.Index(fields=['docto_conta', 'fecha'])  # Índice para acelerar joins
        ]
        db_table = 'hecho_econo'

    def __str__(self):
        return str(self.docto_conta.codigo) + ' ' + str(self.numero)
    

