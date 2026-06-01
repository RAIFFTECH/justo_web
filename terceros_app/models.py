from django.db import models
from multiselectfield import MultiSelectField
from clientes_app.models import CLIENTES
from justo_app.models import validate_numeric, DefaultToZeroMixin
from justo_app.opciones import OPC_BOOL, OPC_REGIMEN, OPC_CLASEDOC, OPC_TIPTER, OPC_VINCULO, OPC_NACIONALIDAD, OPC_GRUPO_ESPECIAL, OPC_ASESORIA
from localidades_app.models import LOCALIDADES
from django.contrib.auth.models import User
import re

class TERCEROS(models.Model):
    id = models.AutoField(primary_key=True) 
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    cla_doc = models.CharField(max_length=1, choices=OPC_CLASEDOC, verbose_name='Tipo Documento')
    nacionalidad = models.CharField(max_length=3, null=True, blank=True, choices=OPC_NACIONALIDAD, default='169', verbose_name='Nacionalidad')
    doc_ide = models.CharField(max_length=12, null=False, verbose_name='Número Documento')
    dig_ver = models.CharField(max_length=1, blank=True,  null=False, verbose_name='DV')
    cod_ciu_exp = models.ForeignKey(LOCALIDADES, on_delete=models.PROTECT, related_name='ciu_exp', null=True, blank=True, verbose_name='Ciudad Expedición Documento')
    fec_exp_ced = models.DateField(null=True, blank=True, verbose_name='Fecha Expedición Documento')
    tip_ter = models.CharField(max_length=1, choices=OPC_TIPTER, verbose_name='Tipo Tercero')
    tip_vinculo = models.CharField(max_length=1, choices=OPC_VINCULO, default='0', verbose_name='Vínculo')
    pri_ape = models.CharField(max_length=28, null=True, verbose_name='Primer Apellido')
    seg_ape = models.CharField(max_length=28, blank=True, null=False, verbose_name='Segundo Apellido')
    pri_nom = models.CharField(max_length=28, null=True, verbose_name='Primer Nombre')
    seg_nom = models.CharField(max_length=28, blank=True, null=False, verbose_name='Segundo Nombre')
    regimen = models.CharField(max_length=12, choices=OPC_REGIMEN, default='49', verbose_name='Tipo Régimen')
    raz_soc = models.CharField(max_length=120, blank=True, null=False, verbose_name='Razón Social')
    direccion = models.CharField(max_length=80, null=False, verbose_name='Dirección')
    celular1 = models.CharField(max_length=10,validators=[validate_numeric],help_text='El número de celular debe contener exactamente 10 dígitos numéricos.', null=True, verbose_name='Celular Principal')
    celular2 = models.CharField(max_length=10, blank=True, null=False, verbose_name='Celular Secundario')
    cod_ciu_res = models.ForeignKey(LOCALIDADES, on_delete=models.PROTECT, related_name='ciu_res', null=True, blank=False, verbose_name='Ciudad Residencia' )
    email = models.EmailField( blank=True, null=False, verbose_name='e-mail')
    tel_ofi = models.CharField(max_length=10, blank=True, null=False, verbose_name='Teléfono Oficina')
    tel_res = models.CharField(max_length=10, blank=True, null=False, verbose_name='Teléfono Residencia')
    cod_pos = models.CharField(max_length=8, blank=True, null=False, verbose_name='Código Postal')
    per_pub_exp = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Persona Expuesta PEP')
    fec_pep = models.DateField(null=True, blank=True, verbose_name='Fecha Inicio PEP')
    cargo_pep = models.CharField(max_length=60, blank=True, null=True, verbose_name='Cargo')
    fec_fin_pep = models.DateField(null=True, blank=True, verbose_name='Fecha Fin PEP')
    grupo_especial = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Pertenece a algún grupo de protección especial constitucional?')
    grupos_especiales = MultiSelectField(null=True, blank=True, choices=OPC_GRUPO_ESPECIAL, max_length=60, verbose_name='Cuáles ?')
    proceso_judicial = models.CharField(null=True, blank=True, max_length=1, choices=OPC_BOOL, default='N', verbose_name='Está vinculado a un proceso judicial penal Ley 1908 2018?')
    fec_act = models.DateField(null=True, blank=True, verbose_name='Fecha Actualización')
    observacion = models.CharField(max_length=255, blank=True, null=False, verbose_name='Observación')
    tipo_asesoria =  models.CharField(max_length=1, blank=True, null=True, choices=OPC_ASESORIA, default='1', verbose_name='Tipo Asesoría')
    usuario_asesor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='usaurio_asesor',verbose_name='Asesor')
    
    nit_rap = models.CharField(max_length=12, blank=True, null=False, verbose_name='Nit Rápido')    
    id_ds = models.BigIntegerField(null=True, blank=True, db_index=True)
    fax = models.CharField(max_length=10, blank=True, null=False, verbose_name='Fax')
    nombre = models.CharField(max_length=120, blank=True, null=True, verbose_name='Nombre')
    nit_interno = models.CharField(max_length=1, choices=OPC_BOOL, blank=True, null=False, verbose_name='Nit Interno')

    def save(self, *args, **kwargs):
        if self.tip_ter.strip().upper() == "N":
            self.nombre = re.sub(r'\s+', ' ', " ".join(filter(None, [self.pri_ape, self.seg_ape, self.pri_nom, self.seg_nom]))).strip()
        else:
            self.nombre = self.raz_soc
        super().save(*args, **kwargs)

    class Meta:
        unique_together = [['cliente', 'doc_ide']]
        indexes = [
        models.Index(fields=['cliente']),
        models.Index(fields=['nombre']),
        ]
        db_table = 'terceros'

    
    def __str__(self):
        return str(self.doc_ide +' - '+ self.nombre)
    