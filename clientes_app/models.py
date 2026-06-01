from django.db import models
import re
from django.core.exceptions import ValidationError
from justo_app.models import validate_numeric,OPC_BOOL,CLASE_COOP

class CLIENTES(models.Model):
    codigo = models.CharField(max_length=1, null=False, verbose_name='Código' )
    doc_ide = models.CharField(max_length=12, validators=[validate_numeric], help_text='El documento de identidad debe ser numérico.', verbose_name='Nit')
    dv = models.CharField(max_length=1, blank=True, null=True, verbose_name='DV')
    sigla = models.CharField(max_length=36, verbose_name='Sigla')
    nombre = models.CharField(max_length=120, verbose_name='Nombre')
    clase_coop = models.CharField(max_length=8,choices=CLASE_COOP,default = 'EAYC', verbose_name='Clase Cooperativa')
    direccion = models.CharField(max_length=128, blank=True, null=True, verbose_name='Dirección')
    telefono = models.CharField(max_length=12, validators=[
                                validate_numeric], help_text='El número de teléfono debe tener solo dígitos numéricos.', blank=True, null=True, verbose_name='Teléfono')
    celular = models.CharField(max_length=10, validators=[
                               validate_numeric], help_text='El número de celular debe contener exactamente 10 dígitos numéricos.', null=True, verbose_name='Celular')
    ciudad = models.CharField(max_length=32, blank=True, null=True, verbose_name='Ciudad')
    email = models.EmailField(verbose_name='E-mail')
    dominio = models.URLField(verbose_name='Dominio')
    nit_ger = models.CharField(max_length=10, validators=[validate_numeric], help_text='El número de documento debe ser numérico.', blank=True, null=True, verbose_name='Documento Gerente')
    nom_ger = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nombre Gerente')
    nit_con = models.CharField(max_length=10, validators=[
                               validate_numeric], help_text='El número de documento debe ser numérico.', blank=True, null=True, verbose_name='Documento Contador')
    nom_con = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nombre Contador')
    tp_con = models.CharField(max_length=16, blank=True, null=True, verbose_name='Tar. Prof. Contador')
    nit_rev_fis = models.CharField(max_length=10, validators=[
                                   validate_numeric], help_text='El número de documento debe ser numérico.', blank=True, null=True, verbose_name='Documento Revisor Fiscal')
    nom_rev_fis = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nombre Revisor Fiscal')
    tp_rev_fis = models.CharField(max_length=16, blank=True, null=True, verbose_name='Tar. Prof. Revisor')
    age_ret = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Agente Retención')
    ret_iva = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Retiene Iva')
    aut_ret = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Autorretenedor')
    logo = models.FileField(max_length=254, null=True, blank=True, verbose_name='Logo')
    num_lic = models.CharField(max_length=8, verbose_name='Número Licencia')
    lic_act = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Licencia Activa')
    ini_lic = models.DateField(null=True,verbose_name='Fecha Incio Licencia')
    fin_lic = models.DateField(null=True,verbose_name='Fecha Fin Licencia')

    class Meta:
        unique_together = [['codigo']]
        db_table = 'clientes'

    def __str__(self):
        return self.sigla + ' ' + self.doc_ide    
    

# class XMOV_CRE(models.Model):
#     id = models.AutoField(primary_key=True)
#     cod_cre = models.CharField(max_length=10, null=False)
#     est_jur = models.CharField(max_length=1, null=False)
#     fecdes = models.DateField(null=True)
#     fec_ult_pag = models.DateField(null=True)
#     min_fecha = models.DateField(null=True)
#     max_fecha = models.DateField(null=True)
#     clase = models.CharField(max_length=1, null=False)
#     docto = models.CharField(max_length=10, null=False)
#     tip_mov = models.CharField(max_length=1, null=False)
#     fecha = models.DateField(null=True)
#     capital = models.FloatField(null=True)
#     int_cor = models.FloatField(null=True)
#     int_mor = models.FloatField(null=True)
#     acreed = models.FloatField(null=True)
#     estado = models.CharField(max_length=1, null=False)
#     class Meta:
#         indexes = [
#             models.Index(fields=['tip_mov']),
#         ]
#         db_table = 'xmov_cre'