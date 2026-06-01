from django.db import models
from oficinas_app.models import OFICINAS, OPC_BOOL

# Create your models here.
class DOCTO_CONTA(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT,verbose_name='Oficina')
    per_con = models.IntegerField(blank=True, null=True,verbose_name='Periodo Contable')
    codigo = models.IntegerField(blank=False, null=False,verbose_name='Código Documento')
    nom_cto = models.CharField(max_length=12, null=False,verbose_name='Nombre Corto')
    nombre = models.CharField(max_length=44, null=False,verbose_name='Nombre Documento')
    doc_admin = models.CharField(max_length=1, blank=True, null=True, choices=OPC_BOOL,verbose_name='Documento Administrativo?')
    doc_caja = models.CharField(max_length=1, blank=True, null=True, choices=OPC_BOOL,verbose_name='Documento de Caja?')
    inicio_nuevo_per = models.CharField(max_length=1, choices=OPC_BOOL,verbose_name='Reinicia Numeración?')
    num_automatico = models.CharField(max_length=1,blank=True,choices=OPC_BOOL,verbose_name='Numeracion Autoatica?')
    consecutivo = models.IntegerField(blank=True, null=True,verbose_name='Consecutivo')
    id_ds = models.BigIntegerField(blank=True, null=True, db_index=True)

    class Meta:
        unique_together = [['oficina', 'per_con', 'codigo']]
        db_table = 'docto_conta'
    
    def __str__(self):
        return self.nombre


class XDOC_ZEP(models.Model):
    per_con = models.IntegerField()
    clase_zep = models.CharField(max_length=1, null=False)
    doc_ds = models.IntegerField(null=True)
    nombre = models.CharField(max_length=16, null=False, blank=True)
    descripcion = models.CharField(max_length=36, null=False, blank=True)

    class Meta:
        unique_together = [['per_con', 'clase_zep']]
        db_table = 'xdoc_zep'
