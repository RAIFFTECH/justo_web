from django.db import models
from justo_app.opciones import OPC_EDUCACION,OPC_BOOL,OPC_EST_CIV,OPC_ESTADO_ANTEIA,OPC_SEXO,OPC_PARENTESCO,OPC_ESTRATO,OPC_ACTIVIDAD_ECON
from justo_app.opciones import OPC_CLASEDOC,OPC_REFERENCIAS,OPC_EST_SOCIO,OPC_ESTADO_ANTEIA, OPC_ZONA,OPC_OCUPACION,OPC_VIVIENDA,OPC_TIPO_SAL
from justo_app.opciones import OPC_TIPO_CONT, OPC_TIPO_PENSION, OPC_DANE
from clientes_app.models import CLIENTES
from ciiu_app.models import CIIU
from oficinas_app.models import OFICINAS
from terceros_app.models import TERCEROS
from localidades_app.models import LOCALIDADES
from pagadores_app.models import PAGADORES 
from justo_app.models import DefaultToZeroMixin
# Create your models here.

class ASOCIADOS(DefaultToZeroMixin):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT, null=True, verbose_name='Oficina')
    cod_aso = models.CharField(max_length=12, null=False, verbose_name='Código Asociado')
    tercero = models.ForeignKey(TERCEROS, on_delete=models.PROTECT, null=True, verbose_name='Tercero')
    estado = models.CharField(max_length=1, choices=OPC_EST_SOCIO, default='A',blank=False, verbose_name='Estado en la Entidad')
    sexo = models.CharField(max_length=1, choices=OPC_SEXO, blank=False, verbose_name='Sexo')
    est_civ = models.CharField(max_length=1, choices=OPC_EST_CIV, verbose_name='Estado Civil')
    fec_nac = models.DateField(null=True, blank=False, verbose_name='Fecha Nacimiento')
    zona = models.CharField(max_length=1, choices=OPC_ZONA, default='U', verbose_name='Zona')
    profesion = models.CharField(max_length=48, null=True, blank=True, verbose_name='Profesión')
    ocupacion = models.CharField(max_length=1, choices=OPC_OCUPACION, verbose_name='Ocupación')
    ocupacion_cod = models.CharField(max_length=3, null=True, blank=True, verbose_name='Código Ocupación')
    estrato = models.CharField(max_length=1, choices=OPC_ESTRATO, verbose_name='Estrato')
    niv_est = models.CharField(max_length=1, choices=OPC_EDUCACION, verbose_name='Nivel de Estudio')
    cab_fam = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Cabeza de Familia?')
    emp_ent = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Empleado de COORINOQUIA?')
    id_pag = models.ForeignKey(PAGADORES, on_delete=models.PROTECT, null=True, verbose_name='Empresa Nominadora')
    fec_afi = models.DateField(null=True, blank=True, verbose_name='Fecha Afiliación')
    fec_ret = models.DateField(null=True, blank=True, verbose_name='Fecha Retiro')
    cargo_emp = models.CharField(max_length=36, null=True, blank=False, verbose_name='Cargo en la Empresa')
    per_a_cargo = models.IntegerField(null=True, blank=False, default='0', verbose_name='Personas a Cargo')
    num_hij_men = models.IntegerField(blank=False, null=True, default='0', verbose_name='Número Hijos Menores')
    num_hij_may = models.IntegerField(blank=False, null=True, default='0', verbose_name='Número Hijos Mayores')
    tip_viv = models.CharField(max_length=1, choices=OPC_VIVIENDA, verbose_name='Tipo de Vivienda')
    tie_en_ciu = models.IntegerField(blank=True, null=True, verbose_name='Tiempo en la Ciudad')
    med_con = models.CharField(max_length=100, null=True, blank=True, verbose_name='med_con')
    fec_ing_tra = models.DateField(null=True, blank=False, verbose_name='Fecha Ingreso Trabajo')
    tel_tra = models.CharField(max_length=10, null=True, blank=True, verbose_name='Teléfono Trabajo')
    tip_sal = models.CharField(max_length=1, null=True, choices=OPC_TIPO_SAL, verbose_name='Tipo de Salario')
    ciu_tra = models.ForeignKey(LOCALIDADES, on_delete=models.PROTECT, related_name='ciu_tra',verbose_name='Ciudad de Trabajo', null=True)
    act_eco = models.CharField(max_length=2, null=True, choices=OPC_ACTIVIDAD_ECON, verbose_name='Actividad Económica')
    cod_ciiu = models.ForeignKey(CIIU, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Código CIIU')
    tip_con = models.CharField(max_length=18, null=True, blank=True, choices=OPC_TIPO_CONT, verbose_name='Tipo Contrato')
    nom_emp = models.CharField(max_length=40, null=True, verbose_name='Nombre Empresa')  
    nit_emp = models.CharField(max_length=12, null=True, verbose_name='Nit Empresa')
    dir_emp = models.CharField(max_length=50, null=True, verbose_name='Dirección Empresa')
    email_emp = models.EmailField(blank=True, null=True, verbose_name='e-mail Empresa')
    sector_emp = models.CharField(max_length=12, null=True, verbose_name='Sector Empresa')
    empresa_ant = models.IntegerField(blank=True, null=True, verbose_name='Empresa Anterior')
    emp_num_emp = models.IntegerField(blank=True, null=True, verbose_name='Numero Empleados')
    negocio_pro = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Negocio Propio?')
    # negocio_nom = models.CharField(max_length=48, null=True, blank=True, verbose_name='Actividad Económica DANE')
    negocio_nom = models.CharField(max_length=48, choices=OPC_DANE, null=True, blank=True, verbose_name='Actividad Económica DANE')
    negocio_tel = models.CharField(max_length=10, null=True, blank=True, verbose_name='Teléfono Negocio')
    negocio_loc_pro = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Local Propio?')
    negocio_cam_com = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Tiene Cámara Comercio?')
    negocio_ant = models.IntegerField(blank=True, null=True, verbose_name='Antiguedad Negocio')
    pension_ent = models.CharField(max_length=36, null=True, verbose_name='Entidad de Pensión')
    pension_tie = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Tiene Pensión?')
    pension_tip = models.CharField(max_length=1, choices=OPC_TIPO_PENSION, default='N', verbose_name='Tipo Pensión?')
    pension_otr = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Otra Pensión?')
    pension_ent_otr = models.CharField(max_length=36, null=True, blank=True, verbose_name='Entidad Otra Pensión')
    pep_es_fam = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Tiene Familiar PEP?')
    pep_fam_par = models.CharField(max_length=1, choices=OPC_PARENTESCO, blank=True, verbose_name='Parentesco Familiar PEP')
    pep_fam_nom = models.CharField(max_length=36, null=True, default='N', verbose_name='Nombre Familiar PEP')
    pep_car_pub = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Tiene Cargo Público PEP?')
    pep_cargo = models.CharField(max_length=36, null=True, default='N', verbose_name='Cargo PEP')
    pep_eje_pod = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='PEP Eje Pod?')
    pep_adm_rec_est = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Administra Recursos del Estado PEP?')
    tie_gre_car = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Tiene Gre Car?')
    recibe_pag_ext = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Recibe Pagos del Extranjero?')
    recide_ext_mas_186 = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Recibe Extranjero +186?')
    recibe_ing_ext = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='Recibe Ingresos Extranjeros?')
    estado_anteia = models.CharField(max_length=1, choices=OPC_ESTADO_ANTEIA, null=False, default=2, verbose_name='Estado Anteia')
    conyuge_nombre = models.CharField(max_length=36, null=True, verbose_name='Nombre Conyuge')
    conyuge_doc_ide = models.CharField(max_length=12, null=True, verbose_name='Doc_ide Conyuge')
    conyuge_trabaja = models.CharField(max_length=1, choices=OPC_BOOL, default='N', verbose_name='conyuge Trabaja?')
    conyuge_ingresos = models.FloatField(blank=True, null=True, verbose_name='Ingresos por Honoarios' ) 
    conyuge_ciudad = models.CharField(max_length=24,blank=True,verbose_name='conyuge Trabaja?')
    conyuge_ocupacion = models.CharField(max_length=30, null=True, verbose_name='Ocupacion Conyuge')
    conyuge_telefono = models.CharField(max_length=12, null=True, verbose_name='Telefono Conyuge')
    conyuge_empresa = models.CharField(max_length=50, null=True, verbose_name='Empresa Conyuge')
    conyuge_dir_empresa = models.CharField(max_length=50, null=True, verbose_name='Empresa Conyuge')
    conyuge_cargo = models.CharField(max_length=50, null=True, verbose_name='Telefono Conyuge')
    conyuge_fec_ing_emp = models.CharField(max_length=4,null=True, verbose_name='agno ing empresas')
    negocio_pro_local = models.CharField(max_length=40,null=True, verbose_name='agno ing empresas')
    barrio_aso = models.CharField(max_length=40,null=True, verbose_name='barrio asociado')
    


    class Meta:
        unique_together = [['oficina', 'cod_aso']]
        db_table = 'asociados'

    def __str__(self):
        return self.cod_aso+' '+self.tercero.nombre

    def get_fields(self):
        fields = []
        for field in self._meta.fields:
            value = getattr(self, field.name)
            fields.append((field.verbose_name, value))
        return fields


class ASO_BENEF(models.Model):
    asociado = models.ForeignKey(ASOCIADOS, on_delete=models.PROTECT, verbose_name='Asociado')
    cla_doc = models.CharField(max_length=1, choices=OPC_CLASEDOC, verbose_name='Clase Documento')
    doc_ide = models.CharField(max_length=12, null=False, verbose_name='Documento')
    nombre = models.CharField(max_length=64, null=False, verbose_name='Nombre Completo')
    agno_nac = models.IntegerField(blank=True, null=True, verbose_name='Año de Nacimiento')
    parentesco = models.CharField(max_length=1, choices=OPC_PARENTESCO, verbose_name='Parentesco')
    porcentaje = models.FloatField(blank=True, null=True, verbose_name='Porcentaje')

    class Meta:
        unique_together = [['asociado', 'doc_ide']]
        db_table = 'aso_benef'
    
    def __str__(self):
        return self.nombre


class ASO_REFERENCIAS(models.Model):
    asociado = models.ForeignKey(ASOCIADOS, on_delete=models.PROTECT, verbose_name='Asociado')
    tipo_ref = models.CharField(max_length=1, choices=OPC_REFERENCIAS, verbose_name='Tipo Referencia')
    parentesco = models.CharField(max_length=1, choices=OPC_PARENTESCO, verbose_name='Parentesco')
    nombre = models.CharField(max_length=64, null=False, verbose_name='Nombre Completo')
    ocupacion = models.CharField(max_length=32, null=False, verbose_name='Ocupación')
    empresa = models.CharField(max_length=40, null=False, verbose_name='Empresa')
    direccion = models.CharField(max_length=64, null=False, verbose_name='Dirección')
    tel_fijo = models.CharField(max_length=10, null=False, verbose_name='Teléfono')
    tel_cel = models.CharField(max_length=10, null=False, verbose_name='Celular')
    tel_emp = models.CharField(max_length=10, null=False, verbose_name='Teléfono Empresa')
    es_fam_dir_cli = models.CharField(max_length=1,choices=OPC_BOOL,default='N', verbose_name='Es familiar de un directivo Entidad')

    class Meta:
        unique_together = [['asociado', 'nombre']]
        db_table = 'aso_referencias'
    
    def __str__(self):
        return self.nombre
