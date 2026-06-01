126991
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
import re
from clientes_app.models import CLIENTES
from oficinas_app.models import OFICINAS
from creditos_app.models import CREDITOS
from django.core.exceptions import ValidationError
from justo_app.opciones import CLASE_COOP, OPC_BOOL, OPC_CAMBIOS_CRE, OPC_CANALES, OPC_CLASEDOC,OPC_CRE_CATEGORIA,OPC_CRE_EST_JUR,OPC_CRE_FOR_PAG,OPC_CRE_TERMINO,OPC_EDUCACION,OPC_EST_CIV,OPC_EST_CRE,OPC_EST_CTA_AHO,OPC_ESTADO_ANTEIA,OPC_GARANTIA,OPC_LIQ_INT_AHO,OPC_MODALIDAD_CRE,OPC_NAT,OPC_NOV_CTA_AHO,OPC_PARENTESCO,OPC_PER_LIQ_INT,OPC_PRODUCTO,OPC_REFERENCIAS,OPC_REGIMEN,OPC_SEXO,OPC_TERMINO,OPC_TIP_CTA,OPC_TIP_MOV_AHO,OPC_TIPTER 


class CARTE_CAT_HIS(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT)
    credito = models.ForeignKey(CREDITOS, on_delete=models.PROTECT, null=True)
    fecha = models.DateField(null=True, blank=True)
    cod_cre = models.CharField(max_length=10, null=True)
    nit = models.CharField(max_length=12, null=True)
    cod_lin_cre = models.CharField(max_length=2, null=True)
    cod_imp_con = models.CharField(max_length=2, null=True)
    for_pag = models.CharField(max_length=1, null=True)
    plazo = models.SmallIntegerField(null=True, default=0)
    dias_mor = models.SmallIntegerField(null=True, default=0)
    cap_ini = models.FloatField(null=True, blank=True, default=0.0)
    sal_cap_dia = models.FloatField(null=True, blank=True, default=0.0)
    sal_int_dia = models.FloatField(null=True, blank=True, default=0.0)
    int_cau_res_per = models.FloatField(null=True, blank=True, default=0.0)
    int_pag_per = models.FloatField(null=True, blank=True, default=0.0)
    int_cor_per = models.FloatField(null=True, blank=True, default=0.0)
    int_conkas_per = models.FloatField(null=True, blank=True, default=0.0)
    cla_gar = models.CharField(max_length=2, null=True, default='  ')
    cat_mor = models.CharField(max_length=1, null=True, default=' ')
    cat_arr = models.CharField(max_length=1, null=True, default=' ')
    cat_mod = models.CharField(max_length=1, null=True, default=' ')
    cat_eva = models.CharField(max_length=1, null=True, default=' ')
    cat_ree = models.CharField(max_length=1, null=True, default=' ')
    cat_sel = models.CharField(max_length=1, null=True, default=' ')
    categoria = models.CharField(max_length=1, null=True, default=' ')
    saldo_1 = models.FloatField(null=True, blank=True, default=0.0)
    saldo_2 = models.FloatField(null=True, blank=True, default=0.0)
    val_gar_hip = models.FloatField(null=True, blank=True, default=0.0)
    cat_int_mes = models.CharField(max_length=1, null=True, default=' ')
    sal_cat_int = models.FloatField(null=True, blank=True, default=0.0)
    sal_int_contin = models.FloatField(null=True, blank=True, default=0.0)
    castigo = models.CharField(max_length=1, null=True, default=' ')
    gas_pro_gen = models.FloatField(null=True, blank=True, default=0.0)
    zeta = models.FloatField(null=True, blank=True, default=0.0)
    puntaje = models.FloatField(null=True, blank=True, default=0.0)
    pro_inc = models.FloatField(null=True, blank=True, default=0.0)
    sal_cap_pe = models.FloatField(null=True, blank=True, default=0.0)
    sal_int_pe = models.FloatField(null=True, blank=True, default=0.0)
    aporte = models.FloatField(null=True, blank=True, default=0.0)
    pdi = models.FloatField(null=True, blank=True, default=0.0)
    vea = models.FloatField(null=True, blank=True, default=0.0)
    per_esp = models.FloatField(null=True, blank=True, default=0.0)
    pro_ind_kap = models.FloatField(null=True, blank=True, default=0.0)
    pro_ind_int = models.FloatField(null=True, blank=True, default=0.0)
    conta_ali = models.SmallIntegerField(null=True, default=0)
    ali_acu = models.FloatField(null=True, default=0.0)
    gas_pro_ind_acu = models.FloatField(null=True, blank=True, default=0.0)
  
    class Meta:
        unique_together = [['oficina', 'fecha', 'cod_cre']]
        indexes = [
            models.Index(fields=['oficina', 'fecha', 'nit']),
            models.Index(fields=['oficina', 'nit','fecha'])
        ]
        db_table = 'carte_cat_his'


class CARTERA_CXC(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT)
    credito = models.ForeignKey(CREDITOS, on_delete=models.PROTECT, null=True)
    cod_cre = models.CharField(max_length=10, null=False)
    fecha = models.DateField(null=False, blank=True)
    fec_ref = models.DateField(null=True, blank=True)
    categoria = models.CharField(max_length=1, null=True)
    valor = models.FloatField(null=True, blank=True)
    val_det = models.FloatField(null=True, blank=True)
    clave = models.SmallIntegerField(null=True)

    class Meta:
        unique_together = [['oficina', 'fecha',
                            'cod_cre', 'fec_ref', 'categoria']]
        db_table = 'cartera_cxc'


class RPKI(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT)
    fecha = models.DateField(null=True, blank=True)
    cod_cre = models.CharField(max_length=10, null=True)
    tipo = models.CharField(max_length=1, null=True)
    nit = models.CharField(max_length=12, null=True)
    fec_des = models.DateField(null=True, blank=True)
    cod_imp = models.CharField(max_length=2, null=True)
    cat_ini = models.CharField(max_length=1, null=True, default=' ')
    cat_fin = models.CharField(max_length=1, null=True, default=' ')
    sal_cap_ini = models.FloatField(null=False, blank=True, default=0.0)
    sal_cap_fin = models.FloatField(null=False, blank=True, default=0.0)
    int_dia_ini = models.FloatField(null=False, blank=True, default=0.0)
    int_cau_ini = models.FloatField(null=False, blank=True, default=0.0)
    inicio = models.FloatField(null=False, blank=True, default=0.0)
    int_pag = models.FloatField(null=False, blank=True, default=0.0)
    int_dia_fin = models.FloatField(null=False, blank=True, default=0.0)
    int_cau_fin = models.FloatField(null=False, blank=True, default=0.0)
    final = models.FloatField(null=False, blank=True, default=0.0)
    int_cau_mes = models.FloatField(null=False, blank=True, default=0.0)
    int_pag_ant = models.FloatField(null=False, blank=True, default=0.0)
    int_pag_act = models.FloatField(null=False, blank=True, default=0.0)
    int_pag_ade = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_A = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_B = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_C = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_D = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_E = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_Z = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_ZC = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_ZD = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_ZE = models.FloatField(null=False, blank=True, default=0.0)
    ip_ant_ZF = models.FloatField(null=False, blank=True, default=0.0)
    cue_pr_cob_A = models.FloatField(null=False, blank=True, default=0.0)
    cue_pr_cob_B = models.FloatField(null=False, blank=True, default=0.0)
    cue_pr_cob_C = models.FloatField(null=False, blank=True, default=0.0)
    cue_pr_cob_D = models.FloatField(null=False, blank=True, default=0.0)
    cue_pr_cob_E = models.FloatField(null=False, blank=True, default=0.0)
    cue_pr_cob_F = models.FloatField(null=False, blank=True, default=0.0)
    cau_ZC = models.FloatField(null=False, blank=True, default=0.0)
    cau_ZD = models.FloatField(null=False, blank=True, default=0.0)
    cau_ZE = models.FloatField(null=False, blank=True, default=0.0)
    cau_ZF = models.FloatField(null=False, blank=True, default=0.0)
    cau_ZET = models.FloatField(null=False, blank=True, default=0.0)
    ingreso = models.FloatField(null=False, blank=True, default=0.0)
    cue_por_pag = models.FloatField(null=False, blank=True, default=0.0)
    cre_con_cas = models.CharField(max_length=1, choices=OPC_BOOL, default=' ')
    int_con = models.FloatField(null=False, blank=True, default=0.0)
    pro_ind_ini = models.FloatField(null=False, blank=True, default=0.0)
    pro_ind_fin = models.FloatField(null=False, blank=True, default=0.0)
    gas_pro_ind_ini = models.FloatField(null=True, blank=True, default=0.0)
    gas_pro_ind_fin = models.FloatField(null=False, blank=True, default=0.0)
    pro_gen_ini = models.FloatField(null=False, blank=True, default=0.0)
    pro_gen_fin = models.FloatField(null=False, blank=True, default=0.0)
    gas_gen_ini = models.FloatField(null=False, blank=True, default=0.0)
    gas_gen_fin = models.FloatField(null=False, blank=True, default=0.0)
    det_ind_gas_acu = models.FloatField(null=False, blank=True, default=0.0)

    class Meta:
        unique_together = [['oficina', 'fecha', 'cod_cre']]
        db_table = 'RPKI'


# Entrega la Calificacion a Partir de un Puntaje por rANGOS
class PE_CALIF_RANGO(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT)
    clase_coop = models.CharField(max_length=8, choices=CLASE_COOP)
    modalidad = models.CharField(
        max_length=6, choices=OPC_MODALIDAD_CRE, default='CCSL')
    calificacion = models.CharField(max_length=1, blank=False)
    pi_puntaje = models.FloatField(null=False, blank=True, default=0.0)

    class Meta:
        unique_together = [
            ['cliente', 'clase_coop', 'modalidad', 'calificacion']]
        db_table = 'pe_calif_rango'

class PE_PI_CALIF(models.Model):  # Recibe la Calificacion y Entrega PI o porcentaje de
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT)
    clase_coop = models.CharField(max_length=8, choices=CLASE_COOP)
    modalidad = models.CharField(max_length=6, choices=OPC_MODALIDAD_CRE, default='CCSL')
    calificacion = models.CharField(max_length=1, blank=False)
    pi_porcent = models.FloatField(null=False, blank=True, default=0.0)

    class Meta:
        unique_together = [
            ['cliente', 'clase_coop', 'modalidad', 'calificacion']]
        db_table = 'pe_pi_calif'

class PE_PDI_RANGO(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT)
    garantia = models.CharField(max_length=2, choices=OPC_GARANTIA, default='15')
    pdi_0 = models.FloatField(null=False, blank=True, default=0.0)
    dias_inc_1 = models.SmallIntegerField(default=0)
    pdi_1 = models.FloatField(null=False, blank=True, default=0.0)
    dias_inc_2 = models.SmallIntegerField(default=0)
    pdi_2 = models.FloatField(null=False, blank=True, default=0.0)

    class Meta:
        unique_together = [['cliente', 'garantia']]
        db_table = 'pe_pdi_rango'

class PE_MODE_REFE(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT)
    modalidad = models.CharField(max_length=6, choices=OPC_MODALIDAD_CRE)
    constante = models.FloatField(null=False, blank=True, default=0.0)
    coe_ea = models.FloatField(null=False, blank=True, default=0.0)
    coe_fe = models.FloatField(null=False, blank=True, default=0.0)
    coe_valcuota = models.FloatField(null=False, blank=True, default=0.0)
    coe_fondplazo = models.FloatField(null=False, blank=True, default=0.0)
    coe_mora1230 = models.FloatField(null=False, blank=True, default=0.0)
    coe_mora1260 = models.FloatField(null=False, blank=True, default=0.0)
    coe_mora2430 = models.FloatField(null=False, blank=True, default=0.0)
    coe_sinmora = models.FloatField(null=False, blank=True, default=0.0)
    coe_mora3660 = models.FloatField(null=False, blank=True, default=0.0)
    coe_mora315 = models.FloatField(null=False, blank=True, default=0.0)

    class Meta:
        unique_together = [['cliente', 'modalidad']]
        db_table = 'pe_mode_refe'

class PE_CARTE_HIS(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT, default=None)
    fecha = models.DateField(null=False, blank=True)
    cod_cre = models.CharField(max_length=10, null=True)
    modalidad = models.CharField(max_length=6, choices=OPC_MODALIDAD_CRE)
    calificacion = models.CharField(max_length=1, null=True)
    pe = models.FloatField(null=False, blank=True, default=0.0)
    pi = models.FloatField(null=False, blank=True, default=0.0)
    vea = models.FloatField(null=False, blank=True, default=0.0)
    pdi = models.FloatField(null=False, blank=True, default=0.0)
    puntaje = models.FloatField(null=False, blank=True, default=0.0)
    z = models.FloatField(null=False, blank=True, default=0.0)
    val_ea = models.SmallIntegerField(default=0)
    val_fe = models.SmallIntegerField(default=0)
    val_valcuota = models.SmallIntegerField(default=0)
    val_fondplazo = models.SmallIntegerField(default=0)
    val_mora315 = models.SmallIntegerField(default=0)
    val_mora1230 = models.SmallIntegerField(default=0)
    val_mora1260 = models.SmallIntegerField(default=0)
    val_mora2430 = models.SmallIntegerField(default=0)
    val_simmora = models.SmallIntegerField(default=0)
    val_mora3660 = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = [['oficina', 'fecha', 'cod_cre']]
        db_table = 'pe_carte_his'
