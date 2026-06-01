import os, django, csv, math
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Justo_proy.settings')
from datetime import timedelta
django.setup()
from django.shortcuts import render
from django.http import HttpResponse
import justo_app.models as justo
from datetime import datetime,timedelta, date
from django.db.models.query import QuerySet
from django.db.models import F, Q, Sum, Case, Max, When, Value, FloatField, CharField, IntegerField, ExpressionWrapper
from django.db.models.functions import Coalesce
from operator import itemgetter
from dateutil.relativedelta import relativedelta
import pandas as pd
from decimal import Decimal, ROUND_DOWN
from io import BytesIO
import numpy as np
from clientes_app.models import CLIENTES
from oficinas_app.models import OFICINAS
from creditos_app.models import CREDITOS
from causacion_creditos_app.models import CREDITOS_CAUSA
from cambios_creditos_app.models import CAMBIOS_CRE
from detalle_producto_app.models import DETALLE_PROD
from centrocostos_app.models import CENTROCOSTOS
from contabilizacion_capital_creditos_app.models import IMP_CON_CRE,MODALIDADES
from asociados_app.models import ASOCIADOS
from terceros_app.models import TERCEROS
from documentos_app.models import DOCTO_CONTA
from hecho_economico_app.models import  HECHO_ECONO
from recla_carte_app.models import PE_CALIF_RANGO, PE_CARTE_HIS, PE_MODE_REFE, PE_PDI_RANGO, PE_PI_CALIF, CARTE_CAT_HIS, CARTERA_CXC,RPKI
from ctas_ahorros_app.models import CTAS_AHORRO
from contabilizacion_intereses_creditos_app.models import IMP_CON_CRE_INT
from cuentas_app.models import PLAN_CTAS
from categorias_creditos_app.models import CAT_DES_DIA_CRE
from detalle_economico_app.models import DETALLE_ECONO
from lineas_credito_app.models import LINEAS_CREDITO
from aportes_app.views import saldo_aporte_socio_fecha

PERIODICIDAD = {
        'SEMANAL': 'E',
        'QUINCENAL': 'U',
        'MENSUAL': 'M',
        'BIMENSUAL': 'B',
        'TRIMESTRAL': 'T',
        'CUATRIMESTRAL': 'C',
        'QUINQUENAL': 'Q',
        'SEMESTRAL': 'S',
        'ANUAL': 'A',
    }

TIPOS_MOV_CRE = {
        'DESEM': 'A',
        'REFIN': '0',
        'CAUSA': '1',
        'AJUST': '2',
        'DESPP': '3',
        'KASCO': '4',
        'CASTI': '5',
        'CONDO': '6',
        'ABOCA': '7',
        'ABOCU': '8',
        'CUOTA': '9'
    }

def asignar_fecha(fecha_str, formato='%m/%d/%Y'):
    try:
        fecha = datetime.strptime(fecha_str, formato)
        fecha_validada = fecha.date()
        return fecha_validada
    except ValueError:
        return None

def truncar(numero, num_decimales):
    return float(Decimal(str(numero)).quantize(Decimal(10) ** -num_decimales, rounding=ROUND_DOWN))

def gomonth(fecha, meses):
    # print('Fecha  ',fecha,'  type  ',type(fecha),'   meses ',meses,'    ',type(meses))
    return fecha + relativedelta(months=meses)

def cargue_mov_cre(iCodCre,valores):
    # Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    Credito = CREDITOS.objects.filter(oficina=Oficina,cod_cre = iCodCre).first()
    valores[0] = Credito.tian_ic_act
    valores[1] = Credito.per_ano
    valores[2] = Credito.cap_ini
    valores[3] = Credito.tian_im
    valores[4] = Credito.por_des_pro_pag
    valores[5] = Credito.per_ano
    valores[6] = Credito.tian_ic_act
    valores[7] = Credito.for_pag
    valores[8] = Credito.fec_des
    valores[9] = Credito.val_cuo_act
    queryset1 = CREDITOS_CAUSA.objects.values('fecha', 'cuota') \
        .filter(oficina=Oficina, cod_cre=Credito.cod_cre,comprobante = None) \
        .annotate(
        tipmov=Value('1'),
        kapital=F('capital'),
        intcor=F('int_cor'),
        intmor=Value(0, output_field=IntegerField()),
        polseg=Value(0, output_field=IntegerField()),
        despp=Value(0, output_field=IntegerField()),
        acreed=Value(0, output_field=IntegerField())
    )
    queryset2 = DETALLE_PROD.objects.filter(oficina=Oficina, producto='CR', subcuenta=Credito.cod_cre) \
        .values(fecha=F('hecho_econo__fecha')) \
        .annotate(
            cuota=Value(0),
            tipmov=Case(
                *[When(concepto=concept, then=Value(value)) for concept, value in TIPOS_MOV_CRE.items()],
                    output_field=CharField()
            ),
            kapital=Coalesce(Sum(Case(When(detalle_econo__item_concepto='Kapita', then=-F('detalle_econo__valor_2')+F('detalle_econo__valor_1')))), Value(0.0)),
            intcor=Coalesce(Sum(Case(When(detalle_econo__item_concepto='IntCor', then=-F('detalle_econo__valor_2')+F('detalle_econo__valor_1')))), Value(0.0)),
            intmor=Coalesce(Sum(Case(When(detalle_econo__item_concepto='IntMor', then=-F('detalle_econo__valor_2')+F('detalle_econo__valor_1')))), Value(0.0)),
            polseg=Coalesce(Sum(Case(When(detalle_econo__item_concepto='PolSeg', then=-F('detalle_econo__valor_2')+F('detalle_econo__valor_1')))), Value(0.0)),
            despp=Coalesce(Sum(Case(When(detalle_econo__item_concepto='DesPP', then=-F('detalle_econo__valor_2')+F('detalle_econo__valor_1')))), Value(0.0)),
            acreed=Coalesce(Sum(Case(When(detalle_econo__item_concepto='Acreed', then=-F('detalle_econo__valor_2')+F('detalle_econo__valor_1')))), Value(0.0)) 
        )
    queryset3 = CAMBIOS_CRE.objects.filter(det_pro__oficina=Oficina, det_pro__producto='CR', det_pro__subcuenta=Credito.cod_cre) \
        .values('fecha') \
        .annotate(
            cuota=Value(0, output_field=IntegerField()),
            tipmov=F('tip_cam'),
            kapital=F('capital'),
            intcor=F('int_cor'),
            intmor=F('int_mor'),
            polseg=F('pol_seg'),
            despp=Value(0, output_field=IntegerField()),
            acreed=F('acreedor')
        )
    tab_liq = list(queryset1) + list(queryset2) + list(queryset3)
    tab_liq = sorted(tab_liq, key = itemgetter('fecha', 'tipmov'))
    # print('tab_liq  ',tab_liq)
    return tab_liq if len(tab_liq)>0 else None
     
#   Calcula el valor de Una cuota a partir de un algoritmo de precision por interpolacion  ciclica  
def calculo_cuota(ikapital,iTIEA,iTIDIC,iPerio,iNumCuo,iFecDes,iFecPagIni,iNumCuoGra=0,iTIDPS=0,iIntCorAnt=0):
    xDias = 0
    xMeses = 0
    if iPerio == 'E':
        xDias = 7
    elif iPerio == 'U':
        xDias = 15
    elif iPerio == 'M':
        xMeses = 1
        xPerAno = 12
    elif iPerio == 'B':
        xMeses = 2
        xPerAno = 6
    elif iPerio == 'T':
        xMeses = 3
        xPerAno = 4
    elif iPerio == 'C':
        xMeses = 4
        xPerAno = 3
    elif iPerio == 'Q':
        xMeses = 5
        xPerAno = 5/12
    elif iPerio == 'S':
        xMeses = 6
        xPerAno = 2
    elif iPerio == 'A':
        xMeses = 12
        xPerAno = 1
    if iTIEA == 0:
        return(int(ikapital/iNumCuo)+1)
    iTIEA = round(iTIEA,4)
    if xMeses != 0:
        xTasPer = round((iTIEA+1)**(1/xPerAno)-1,4)
    elif xDias == 7:
        xTasPer = round((iTIEA+1)**(1/52.1428)-1,4)
    elif xDias == 15:
        xTasPer = round((iTIEA+1)**(1/24)-1,4)
    xValCuo = int(ikapital*xTasPer/round(1-(1+xTasPer)**(-iNumCuo),4)+1)
    xCiclos = 0
    x0 = xValCuo
    while True:
        xCiclos = xCiclos + 1
        xFecAnt = iFecDes
        xFecPagFin = iFecDes
        xSaldo = ikapital
        xFecCuo = iFecPagIni
        xIntPorApl = iIntCorAnt
        xIntApl = 0
        for xPer in range(1,iNumCuo+iNumCuoGra+1):
            xDifDias = (xFecCuo-xFecAnt).days
            xIntIC = round(xSaldo * iTIDIC * 1000,0)
            xIntIC = round(xIntIC/1000,0)*xDifDias
            xIntPS = round(xSaldo * iTIDPS * 1000,0)*(xDifDias)
            xIntPS = round(xIntPS/1000,0)*(xDifDias)
            xIntPer = xIntIC + xIntPS + xIntPorApl
            xCapPer = round(xValCuo-xIntApl-xIntPer if xPer > iNumCuoGra and xValCuo-xIntApl-xIntPer > 0 else 0)
            xNueCapPer = xCapPer 
            # xCapPer= xCapPer + si tiene cuotas extras  
            xIntApl = xIntApl + (xIntPer if xPer < iNumCuoGra else 0)
            xIntApl = xIntApl + (xValCuo - xNueCapPer - xIntPer if xIntPorApl > 0 else 0)
            xIntApl = xIntApl if xIntApl > 0 else 0
            #xIntPorApl = xIntPorApl - xIntPer
            xFecAnt = xFecCuo
            xSaldo = xSaldo - xCapPer 
            xFecPagFin = xFecCuo
            if xMeses > 0 :
                xFecCuo = gomonth(iFecPagIni,xMeses*xPer)
            elif iPerio == 'E':
                xFecCuo = xFecCuo + 7
            elif  xPer % 2 == 1:
                xFecCuo = xFecCuo + 15
            else:
                xFecCuo = gomonth(xFecCuo-15,1)
        if ((xSaldo > -(iNumCuo+iNumCuoGra)*3) or xCiclos  >= 10) and (xSaldo < 1): 
    #    or round(xSaldo/(iNumCuo+iNumCuoGra),0) == 0):   ojo cambios oct 10 de 2024
            break
        if xCiclos == 1:
            y0 = xSaldo
            xValCuo = xValCuo + round(xSaldo/(iNumCuo+iNumCuoGra),0)
            x1 = xValCuo
        else:
            y1 = xSaldo
            if y1 == y0:
                xValCuo = xValCuo + (1 if y1 < 0 else -1)
            else:
                xValCuo = round(x1 - y1*(x1-x0)/(y1-y0),0)
            if xValCuo == x1:
                xValCuo = xValCuo + (1 if xSaldo > 0 else -1)
            x0 = x1
            x1 = xValCuo
            yo = y1
    return(xValCuo)

class Liquida_cre:
    cod_cre = ''
    cap_ini = 0
    fecha_focal = None
    lista_mov = []
    val_cuo = 0
    fec_des = None
    for_pag = ' '
    sal_cap_tot = -1
    sal_cap_dia = -1
    sal_int_dia = -1
    sal_ps_dia = -1
    sal_int_mor = -1
    int_cau_fra = -1
    int_aju_pa = -1
    int_pag_tot = 0
    altura = -1
    cuo_pag = -1
    cuo_pac = -1
    fec_al_dia = None
    fec_ven = None
    tas_ic_ea = 0.0
    tas_ic_dia = 0.0
    tas_im_anual = 0.0
    por_des_pp = 0.0
    per_ano = 0
    tip_pag = ''
    capital_a_pag = 0
    int_cor_a_pag = 0
    pol_seg_a_pag = 0
    int_mor_a_pag = 0
    acreedor_a_pag = 0
    int_mor_cau = -1
    aju_cap_a_pag = 0
    aju_ic_a_pag = 0
    aju_ps_a_pag = 0
    aju_im_a_pag = 0
    max_pag_couta = 0
    min_pag_aboca = 0
    min_pag_abocu = 0
    fec_sig_pag1 = None
    fec_sig_pag2 =None
    tip_pag = 'DESEM'
    int_pag_per = 0
    int_condo = 0
    int_mor_ya_pag = 0
    
    def __init__(self, iCodCre, iFecha_Focal = datetime.now().date()):     #  se inicializa los parametros iniciales 
        self.cod_cre = iCodCre
        self.fecha_focal = iFecha_Focal 
        params = [0.0,0,0,0.0,0.0,0,0.0,' ',date(1900,1,1),0]
        self.lista_mov = cargue_mov_cre(iCodCre,params)                    #  Se estructuran los movimientos para la liquidacion 
        if self.lista_mov == None:
            return 
        self.cap_ini = params[2]
        xTasIntPer = round((params[0]/100+1)**(1/params[1])-1,6)
        self.tas_ic_dia = round(xTasIntPer*params[1]*100/36525,6)

        self.tas_im_anual = params[3]
        self.por_des_pp = params[4]
        self.per_ano = params[5]
        self.tas_ic_ea = params[6]
        self.for_pag = params[7]
        self.fec_des = params[8]
        self.fec_al_dia = params[8]
        self.val_cuo = params[9]
        self.fec_ven = params[8]
        self._calculos_generales()
        return 
 
    def _calculos_generales(self):                      #  Para conocer fecha de vencimiento 
        xCapIni = 0
        xCapCau = 0
        xCapPag = 0
        self.sal_cap_tot = 0
        self.sal_cap_dia = 0
        xFecPag = None
        for reg in self.lista_mov:
            if reg['tipmov'] == 'A':
                self.fec_des = reg['fecha']
                self.fec_al_dia = reg['fecha']
            #    self.cap_ini = reg['kapital']  
                continue
            self.sal_cap_tot = self.sal_cap_tot + (reg['kapital'] if (reg['fecha'] - self.fecha_focal).days <= 0 or reg['tipmov'] == '0' or reg['tipmov'] == '1' else 0)
            #print('Fecha  ',reg['fecha'],'   kapital',reg['kapital'],'     Sal_cap_tot ', self.sal_cap_tot )
            xCapPag = xCapPag + (reg['kapital'] if reg['fecha'] <= self.fecha_focal and reg['tipmov'] != '1' else 0)
            self.sal_cap_dia = self.sal_cap_dia + (reg['kapital'] if reg['fecha'] <= self.fecha_focal else 0)
            if reg['fecha'] <= self.fecha_focal and reg['tipmov'] == '1':
                self.altura = reg['cuota']
        xYaApl = False
        for reg in self.lista_mov:
            if reg['tipmov'] == 'A':
                continue
            if reg['tipmov'] == '0' or reg['tipmov'] == '1':
                xCapCau = xCapCau + reg['kapital']
                if xCapCau + xCapPag > 0:
                    if xYaApl == False:
                        self.fec_al_dia = reg['fecha']
                        self.cuo_pag = reg['cuota'] - 1
                        xYaApl = True
                else:
                    xYaApl = False
            if reg['kapital'] > 0 and reg['intcor'] != 0:
                self.cuo_pac = reg['cuota']
                self.fec_ven = reg['fecha']

    def calculo_periodo(self):
        self.int_pag_per = 0
        self.int_condo = 0
        lista_periodo = [objeto for objeto in self.lista_mov if objeto['fecha'].year == self.fecha_focal.year and objeto['fecha'].month == self.fecha_focal.month and objeto['tipmov'] > '3']
        for reg in lista_periodo:
            if reg['tipmov'] > '3':
                self.int_pag_per = self.int_pag_per - reg['intcor']
            else:
                self.int_condo = self.int_condo = 0 - reg['intcor']
        return

    def liq_al_dia(self,ifecha_focal = datetime.now().date(),recarga = False):
        if self.fecha_focal != ifecha_focal and recarga == True:
            self.fecha_focal = ifecha_focal 
            params = [0.0,0,0,0.0,0.0,0,0.0,' ',date(1900,1,1),0]
            self.lista_mov = cargue_mov_cre(self.cod_cre,params)
            self._calculos_generales()
        self.sal_int_dia = 0
        self.sal_int_mor = 0
        self.int_mor_cau = 0
        self.sal_ps_dia = 0
        self.int_cau_fra = 0
        self.int_aju_pa = 0
        self.int_pag_tot = 0
        oIntPagTot = 0    #  sirve  no 
        oIntAjuAboCap = 0
        xDiaConIntMor = 0
        xSalPro = xSalRea = xSalProDia = xSalReaDia = self.cap_ini
        xFecCer = self.fec_des
        xFecUltPag = xFecCer
        xFecUltCau = xFecCer
        xFecCauCapNeg = datetime(1900, 1, 1).date()
        xFecRefMor = self.fecha_focal + timedelta(days=1)
        xSalCuoPag = 0
        lista_al_dia = [objeto for objeto in self.lista_mov if objeto['fecha'] <= self.fecha_focal and objeto['tipmov'] != 'A']
        for reg in lista_al_dia:
            self.sal_int_dia = self.sal_int_dia + reg['intcor']
            #print('Fecha ',self.sal_int_dia)
            self.sal_int_mor = self.sal_int_mor + reg['intmor']
            self.sal_ps_dia = self.sal_ps_dia + reg['polseg']
            if reg['tipmov'] == '0' or reg['tipmov'] == '1':
                xFecUltCau = reg['fecha'] 
                if reg['fecha'] < self.fecha_focal:
                    xSalPro = xSalPro - reg['kapital']
                if reg['kapital'] < 0:
                    xFecCauCapNeg = reg['fecha'] 
            else:
                if reg['tipmov'] >= '4': 
                    #print('vence  ',self.fec_ven)
                    xFecUltPag = reg['fecha'] if reg['fecha'] <= self.fec_ven else self.fec_ven
                    xFecRefMor = reg['fecha']
                    xSalCuoPag = xSalCuoPag + reg['kapital']
                    oIntPagTot = oIntPagTot - reg['intcor']
        self.int_pag_tot = oIntPagTot 
        xFecAntMov = xFecUltCau
        xSalReaAnt = xSalRea
        oIntPagPosDia = 0
        xYaAjuIntAnt = False
        for reg in lista_al_dia:
            if reg['tipmov'] == '3' and reg['fecha'] > xFecUltCau and reg['fecha'] >= xFecUltPag and xFecUltPag <= self.fecha_focal and xFecUltPag >= xFecUltCau:
                #print('Fecha ',reg['fecha'],' oIntAjuAboCap',oIntAjuAboCap,' reg[intcor]  ',reg['intcor'],' xFecUltCau ',xFecUltCau,'  xFecUltPag  ',xFecUltPag)
                oIntAjuAboCap = oIntAjuAboCap - (reg['intcor'] if reg['intcor'] < 0 else 0)
            if reg['fecha'] <= xFecUltCau:
                xSalProDia = xSalProDia - (reg['kapital'] if reg['tipmov'] == '1' else 0)
                xSalReaDia = xSalReaDia + (reg['kapital'] if reg['tipmov'] >= '4' else 0)
                if reg['fecha'] == xFecUltCau and reg['tipmov'] == '2':     #  se cambia 4 por 2 por ser ajuste descubierto el 16 de abril de 2025
                    xYaAjuIntAnt = True
                else:
                    oIntPagPosDia = oIntPagPosDia- (reg['intcor'] if reg['tipmov'] else 0)
            if  reg['tipmov'] >= '4': 
                xSalReaAnt = xSalRea
                xSalRea = xSalRea + reg['kapital']
                if reg['fecha'] > xFecUltCau: 
                    self.int_cau_fra = self.int_cau_fra + int((xSalPro if xSalPro <= xSalRea else (xSalPro if xSalPro <= xSalReaAnt else xSalReaAnt))*(reg['fecha']-xFecAntMov).days*self.tas_ic_dia)
                    xFecAntMov = reg['fecha']
            if  reg['tipmov'] == '1': 
                if xSalCuoPag < 100:
                    oFecUltCuoPag = reg['fecha']
                xSalCuoPag = xSalCuoPag + reg['kapital']
                if  reg['fecha'] > xFecCauCapNeg:  
                    if xSalCuoPag > 0:
                        if reg['fecha'] <= xFecRefMor and xFecRefMor <= self.fecha_focal:
                            xDiaMor = ((self.fecha_focal-xFecRefMor).days if (xFecRefMor-reg['fecha']).days > xDiaConIntMor else (self.fecha_focal-reg['fecha']).days)
                            xDiaMor = xDiaMor if (self.fecha_focal-reg['fecha']).days > xDiaConIntMor else 0 
                        else:
                            xDiaMor = (self.fecha_focal - reg['fecha']).days
                            xDiaMor = xDiaMor if xDiaMor > xDiaConIntMor else 0
                        self.int_mor_cau = self.int_mor_cau + round((reg['kapital'] if xSalCuoPag > reg['kapital'] else xSalCuoPag)*xDiaMor*self.tas_im_anual/36525,0)
        if (self.fecha_focal - xFecAntMov).days > 0:
            self.int_cau_fra = self.int_cau_fra + int((xSalPro if xSalPro < xSalRea else xSalRea)*(self.fecha_focal-xFecAntMov).days*self.tas_ic_dia)
        
    #    print('xSalProDia ',xSalProDia,' xSalReaDi',xSalReaDia)
        xBasCapAju = xSalProDia - xSalReaDia
        xBasCapAju  = 0 if xYaAjuIntAnt else xBasCapAju
    #  la siGuiEnte inStyruCion es nueva a 14 de abril dE 2925 por Que la anteRior estabA mal    
        lista_pos_dia = [objeto for objeto in self.lista_mov if objeto['fecha'] > self.fecha_focal and objeto['tipmov'] != 'A']
        for reg in lista_pos_dia:
            if reg['tipmov'] == '1':
                if xBasCapAju > 0:
                    xBasCap = reg['kapital'] if reg['kapital'] < xBasCapAju else xBasCapAju
                    self.int_aju_pa = self.int_aju_pa + round(xBasCap*(reg['fecha']-xFecUltCau).days*self.tas_ic_dia,0)
                    xBasCapAju = xBasCapAju - xBasCap
                xSalPro = xSalPro - reg['kapital']
                if xSalCuoPag < 100:
                    oFecUltCuoPag = reg['fecha']
                xSalCuoPag = xSalCuoPag + reg['kapital']
        self.capital_a_pag = self.sal_cap_dia
        self.int_cor_a_pag = self.sal_int_dia
        self.pol_seg_a_pag = self.sal_ps_dia
        self.int_mor_a_pag = self.int_mor_cau if self.for_pag == 'P' else 0
        lista_final = [objeto for objeto in self.lista_mov if objeto['fecha'] > self.fecha_focal and objeto['tipmov'] == '1']
        xSig = 0
        xPagCapAdi = 0
        xPagAdiIc = 0
        for reg in lista_final:
            if xSig == 0:
                xPagCapAdi = reg['kapital'] 
                xPagAdiIc =  reg['intcor']
                self.fec_sig_pag1 = reg['fecha']
                xDia1 = (self.fec_sig_pag1 - self.fecha_focal).days
                xMaxSaldo = self.val_cuo / (self.tas_ic_dia*xDia1) 
                self.min_pag_aboca = self.int_cor_a_pag + self.pol_seg_a_pag + self.int_mor_a_pag +self.int_cau_fra
                self.min_pag_aboca = self.min_pag_aboca + (self.sal_cap_dia if self.sal_cap_tot - self.sal_cap_dia < xMaxSaldo else  xMaxSaldo - self.sal_cap_tot)
            elif xSig == 1:
                xPagCapAdi = xPagCapAdi + reg['kapital'] 
                xPagAdiIc = xPagAdiIc + reg['intcor']
                self.fec_sig_pag2 = reg['fecha']
                xDia2 = (self.fec_sig_pag2 - self.fecha_focal).days
                xMaxSaldo = self.val_cuo / (self.tas_ic_dia*xDia2) 
                self.min_pag_abocu = self.int_cor_a_pag + self.pol_seg_a_pag + self.int_mor_a_pag +self.int_cau_fra
                self.min_pag_abocu = self.min_pag_abocu + (self.sal_cap_dia if self.sal_cap_tot - self.sal_cap_dia < xMaxSaldo else  xMaxSaldo - self.sal_cap_tot)
                self.max_pag_couta = int(xPagCapAdi + xPagAdiIc + self.capital_a_pag + self.int_cor_a_pag + self.pol_seg_a_pag - xPagCapAdi*self.tas_ic_dia*xDia2 )
            else:
                break
            xSig = xSig + 1 
        # self.sal_int_dia = self.sal_int_dia + oIntAjuAboCap   se encontro en abril 14  algo hay que hacer con oIntAjuAboCap
        # print('Fecha ',self.sal_int_dia,' oIntAjuAboCap ',oIntAjuAboCap)
        self.sal_int_dia = self.sal_int_dia + oIntAjuAboCap

    def liq_por_cuotas(self,iAltura):
        tip_pag = 'CUOTA'
        xDiaConIntMor = 0
        xCapIni = self.cap_ini
        xSalPro = self.cap_ini
        xSalRea = xSalPro
        xFecCer = self.fec_des
        xFecUltPag = self.fecha_focal + timedelta(days=1)
        xFecUltCau = xFecCer
        Anticipo = True
        xCapPag = xIntPag = xMorPag = xPolSegPag = xMorCau = 0
        lista_al_dia = [objeto for objeto in self.lista_mov if objeto['fecha'] <= self.fecha_focal and objeto['tipmov'] != 'A']
        for reg in lista_al_dia:
            if reg['tipmov'] != '1' :
                xSalRea = xSalRea + reg['kapital']
                xCapPag = xCapPag - reg['kapital']
                xIntPag = xIntPag - reg['intcor']
                xMorPag = xMorPag - (reg['intmor'] if reg['tipmov'] >= '4' else 0)
                xMorCau = xMorCau + (reg['intmor'] if reg['tipmov'] == '3' else 0)
                xPolSegPag = xPolSegPag - reg['polseg']
                xFecUltPag = reg['fecha']
            else:
                if reg['fecha'] < self.fecha_focal:
                    xSalPro = xSalPro - reg['kapital']
        xCapMor = -xCapPag
        xMorAnt = 0
        xMorAcu = xMorCau - xMorPag
        xMorYaPag = 0
        if xFecUltPag <= self.fecha_focal:
            for reg in lista_al_dia:
                if reg['tipmov'] == '1' :
                    xCapMor = xCapMor + reg['kapital']
                    xMorAcu = xMorAcu + reg['intmor']
                    if xCapMor > 0:
                        xDiaMor1 = ((self.fecha_focal if xFecUltPag > self.fecha_focal else xFecUltCau) - reg['fecha']).days
                        xDiaMor1 = xDiaMor1 if xDiaMor1 > xDiaConIntMor else 0
                        xMorAnt = xMorAnt + round(reg['kapital'] if xCapMor > reg['kapital'] else xCapMor*xDiaMor1*self.tas_im_anual/36525,0)
            xMorYaPag = xMorAnt - xMorAcu
        xCapCau = xIntCau = xPolSegCau = 0
        xMorCauCuo = 0
        xFecUltPer = xFecCer
        for reg in lista_al_dia:
            if reg['tipmov'] == '1' :
                xCapCau = xCapCau + reg['kapital']
                xIntCau = xIntCau + reg['intcor']
                xPolCau = xPolSegCau + reg['polseg']
                if xCapCau >= xCapPag:
                    oCapital = xCapCau - xCapPag
                    oIntCor = xIntCau - xIntPag
                    oIntMor = xMorCau - xMorPag
                    oPolSeg = xPolSegCau - xPolSegPag
                    if reg['fecha'] == self.fecha_focal:
                        xSalPro = xSalPro - reg['kapital']
                    if reg['fecha'] <= xFecUltPag:
                        xDiaMor1 = ((self.fecha_focal if xFecUltPag > self.fecha_focal else xFecUltPag)- reg['fecha']).days
                        xDiaMor1 = xDiaMor1 if xDiaMor1 > xDiaConIntMor else 0
                        xDiaMor2 = (self.fecha_focal - xFecUltPag).days if oCapital > reg['kapital'] else 0
                        xMorCauAnt = round((reg['kapital'] if oCapital > reg['kapital']  else oCapital)*xDiaMor1*self.tas_im_anual/36525,0)
                        if xMorYaPag > 0:
                            if xMorYaPag > xMorCauAnt:
                                xMorYaPag = xMorYaPag - xMorCauAnt
                                xMorCauAnt = 0
                            else:
                                xMorCauAnt = xMorCauAnt - xMorYaPag
                                xMorYaPag = 0
                        xMorCauPer = xMorCauAnt + round((reg['kapital'] if oCapital > reg['kapital'] else oCapital)*xDiaMor2*self.tas_im_anual/36525,0)
                        xDiaMor = (self.fecha_focal - reg['fecha']).days if xFecUltPag > self.fecha_focal else (self.fecha_focal - xFecUltPag).days
                        xMorCauCuo = xMorCauCuo + xMorCauPer
                    else:
                        xDiaMor = (self.fecha_focal - reg['fecha']).days if (self.fecha_focal - reg['fecha']).days > xDiaConIntMor  else 0
                        xMorCauPer = round((reg['kapital'] if oCapital > reg['kapital'] else oCapital)*xDiaMor*self.tas_im_anual/36525,0)
                        xMorCauCuo = xMorCauCuo + xMorCauPer
                    if reg['cuota'] == iAltura:
                        Anticipo = False
                        break
            xFecUltPer = reg['fecha']
        oCapital = xCapCau - xCapPag
        oIntCor = xIntCau - xIntPag
        oIntMor = xMorCauCuo
        oPolSeg = xPolSegCau - xPolSegPag
        oIntAnt = 0
        if Anticipo :
            lista_al_dia = [objeto for objeto in self.lista_mov if objeto['fecha'] > self.fecha_focal]
            for reg in lista_al_dia:
                oCapital = oCapital + reg['kapital'] 
                oIntCor = oIntCor + reg['intcor'] 
                oIntMor = oIntMor + reg['intmor'] 
                oPolSeg  = oPolSeg + reg['polseg'] 
                if reg['tipmov'] == '1':
                    xCapPer = oCapital if oCapital < reg['kapital'] else reg['kapital']
                    xCapPer = xCapPer if xCapPer > 0 else 0
                    xIntPer = oIntCor if oIntCor < reg['intcor'] and oIntCor >= 0 else (0 if oIntCor < 0  else reg['intcor'])
                    xFacInt = ((reg['fecha']-self.fecha_focal).days if (reg['fecha']-self.fecha_focal).days > 0 else 0)*self.tas_ic_dia
                    xConIntAnt = round(xCapPer*self.tas_ic_dia,0)*((reg['fecha']-self.fecha_focal).days if (reg['fecha']-self.fecha_focal).days > 0 else 0)
                    oIntAnt = oIntAnt + xConIntAnt
                    if reg['cuota'] == iAltura:
                        break
        self.capital_a_pag = oCapital
        self.int_cor_a_pag = oIntCor
        self.pol_seg_a_pag = oPolSeg
        self.int_mor_a_pag = oIntMor if self.for_pag == 'P' else 0
        self.acreedor_a_pag = 0
        self.int_mor_cau = 0
        self.aju_ic_a_pag = 0

    def distri_pago_cuota(self,iValPorDis):
        self.tip_pag = TIPOS_MOV_CRE['CUOTA']
        oAboCap = oAboIntCor = oAboIntMor = oAboPolSeg = oConIntAnt = oCauIntMor = oSalTot = zConIntAnt = 0
        oSalTot = self.cap_ini
        xSalPro = oSalTot
        xSalRea = xSalPro
        xDiaConIntMor = 0
        xFecCer = self.fec_des
        xTasIntPer = round((round(self.tas_ic_ea/100,4)+1)**(1/self.per_ano),4)
        xTasDesIntPer = 0
        xFecUltPag = xFecCer - timedelta(days=1)
        xFecUlpPagMor = xFecCer - timedelta(days=1)
        xAboCap = xAboIntCor = xAboIntMor = xAboPolSeg = xMenosUltPag = xMorYaPag = 0
        xFecCauCapNeg = datetime(1900, 1, 1).date()
        lista_al_dia = [objeto for objeto in self.lista_mov if objeto['fecha'] <= self.fecha_focal and objeto['tipmov'] != 'A']    
        for reg in lista_al_dia:
            if reg['tipmov'] != '1':
                xSalRea = xSalRea + reg['kapital']
                oSalTot = oSalTot + reg['kapital']
                xAboCap = xAboCap + reg['kapital']
                xAboIntCor = xAboIntCor + reg['intcor']  
                xAboIntMor = xAboIntMor + reg['intmor']
                xAboPolSeg = xAboPolSeg + reg['polseg']
                if reg['tipmov'] >= "5":
                    xFecUltPag = reg['fecha']
                    xMenosUltPag = reg['kapital']
            else:  
                if reg['kapital'] < 0:
                    xFecCauCapNeg = reg['fecha']
                if reg['fecha'] < self.fecha_focal:
                    xSalPro = xSalPro - reg['kapital']
            if reg['tipmov'] == '3':
                xMorYaPag = reg['acreed'] 

        
        xAntAboCap = xAboCap - xMenosUltPag
        xSalPorDis = iValPorDis
        oAboIntMor = 0
        self.int_mor_ya_pag = 0

#  * aqui Comienzan las aplicaciones de pagos
        lista_al_dia = [objeto for objeto in self.lista_mov if objeto['fecha'] <= self.fecha_focal and objeto['tipmov'] == '1']    
        for reg in lista_al_dia:
            xAboCap = xAboCap + reg['kapital']
            xAntAboCap = xAntAboCap + reg['kapital']
            xAboIntCor = xAboIntCor + reg['intcor']
            xAboIntMor = xAboIntMor + reg['intmor']
            xAboPolSeg = xAboPolSeg + reg['polseg']
            if xAboCap > 0 or xAboIntCor > 0 or xAboPolSeg > 0:
                if reg['fecha'] == self.fecha_focal:
                    xSalPro = xSalPro - reg['kapital']
                xCapPer = xAboCap
                xIntPer = xAboIntCor if xAboIntCor > 0 else 0
                xPolSegPer = xAboPolSeg if xAboPolSeg > 0 else xAboPolSeg
                xIntMorDes = 0
                if not (reg['fecha'] + timedelta(days=35) > xFecCauCapNeg  and  reg['fecha'] < xFecCauCapNeg):
                    if reg['fecha'] < xFecUltPag:
                        if xFecUltPag > self.fecha_focal:
                            xDiaMor1 = 0
                            xMorCauAnt = 0
                            xDiaMor2 = (self.fecha_focal - reg['fecha']).days
                            xDiaMor2 = xDiaMor2 if xDiaMor2 > xDiaConIntMor else 0
                            xMorCauNvo = round((reg['fecha'] if xCapPer > reg['fecha'] else xCapPer) * xDiaMor2*(self.tas_im_anual/36525),0)
                        else:
                            xDiaMorIni = (xFecUltPag - reg['fecha']).days
                            xDiaMor1 = xDiaMorIni
                            #xDiaMor1 = xDiaConIntMor if xDiaMor1 > xDiaConIntMor else 0  julio 20 2025 error 
                            xDiaMor1 = xDiaMor1 if xDiaMor1 > xDiaConIntMor else 0
                            if xAntAboCap > 0:
                                xMorCauAnt = round((reg['kapital'] if xAntAboCap > reg['kapital'] else xAntAboCap)*xDiaMor1*(self.tas_im_anual/36525),0)
                            else:
                                xMorCauAnt = 0
                            xDiaMor2 = (self.fecha_focal - xFecUltPag).days + (xDiaMorIni if xDiaMorIni != xDiaMor1 else 0)
                            xDiaMor2 = xDiaMor2 if xDiaMor2 > xDiaConIntMor else 0
                            xMorCauNvo = round((reg['kapital'] if xCapPer > reg['kapital'] else xCapPer)*xDiaMor2*(self.tas_im_anual/36525),0)
                        xMorCauAnt = 0 if reg['fecha'] <= xFecUlpPagMor else xMorCauAnt
                        if xMorYaPag > 0:
                            if xMorYaPag > xMorCauAnt:
                                xIntMorDes = xMorCauAnt 
                                xMorYaPag = xMorYaPag - xMorCauAnt
                                xMorCauAnt = 0
                            else:
                                xIntMorDes = xMorYaPag 
                                xMorCauAnt = xMorCauAnt-xMorYaPag
                                xMorYaPag = 0
                        xMorCauPer = xMorCauAnt + xMorCauNvo   # jul-20-2025
                        #   xMorCauPer = xAboIntMor + xMorCauNvo
                        oCauIntMor = oCauIntMor + xMorCauNvo
                    else:
                        xDiaMor = (self.fecha_focal - reg['fecha']).days
                        xDiaMor = xDiaMor if xDiaMor > xDiaConIntMor else 0
                        xMorCauPer = round((reg['kapital'] if xCapPer > reg['kapital'] else xCapPer)*xDiaMor*(self.tas_im_anual/36525),0)
                        oCauIntMor = oCauIntMor + xMorCauPer  
                else:
                    xMorCauNvo = 0
                    xMorCauPer = 0
#   significa QUE DE AQUI EN ADELANTE SIEMRE HAY DEUDA Y SE APLICA EL PAGO MIENTRAS HAYA SALDO
                xPrimero = True
                for rega in lista_al_dia[lista_al_dia.index(reg):]:
                    if xSalPorDis <= 0:
                        break
                    if xPrimero == False :
                        xAboCap = xAboCap + rega['kapital']
                        xAntAboCap = xAntAboCap + rega['kapital']
                        xAboIntCor = xAboIntCor + rega['intcor']  
                        xAboIntMor =xAboIntMor + rega['intmor']
                        xAboPolSeg = xAboPolSeg + rega['polseg']
                        xCapPer = rega['kapital'] if rega['kapital'] < xAboCap else xAboCap
                        xCapPer = xCapPer if xCapPer > 0 and xFecCauCapNeg < self.fecha_focal else 0
                        xIntPer = rega['intcor'] if rega['intcor'] < xAboIntCor else xAboIntCor
                        xIntPer = xIntPer if xIntPer > 0 else 0
                        if rega['fecha'] == self.fecha_focal:
                            xSalPro = xSalPro - rega['kapital']
                        xPolSegPer = rega['polseg'] if rega['polseg'] < xAboPolSeg else xAboPolSeg
                        xPolSegPer = xPolSegPer if xPolSegPer > 0 else 0        
                        xIntMorDes=0 
                        if rega['fecha'] <= xFecUltPag:
                            if xFecUltPag > self.fecha_focal:
                                xDiaMor1 = 0
                                xDiaMor2 = (self.fecha_focal- rega['fecha']).days
                            else:
                                xDiaMor1 = (xFecUltPag - rega['fecha']).days
                                xDiaMor2 = (self.fecha_focal - xFecUltPag).days + (xDiaMor1 if xDiaMor1 <= xDiaConIntMor else 0)
                            xDiaMor1 = xDiaMor1 if xDiaMor1 > xDiaConIntMor else 0
                            if xAntAboCap > 0:
                                xMorCauAnt = round((rega['kapital'] if xAntAboCap > rega['kapital'] else xAntAboCap)*xDiaMor1*(self.tas_im_anual/36525),0)
                            else:
                                xMorCauAnt = 0
                            if xMorYaPag > 0:
                                if xMorYaPag > xMorCauAnt:
                                    xIntMorDes = xMorCauAnt
                                    xMorYaPag = xMorYaPag-xMorCauAnt
                                    xMorCauAnt = 0
                                else:
                                    xIntMorDes = xMorYaPag 
                                    xMorCauAnt = xMorCauAnt - xMorYaPag
                                    xMorYaPag = 0
                            xDiaMor2 = xDiaMor2 if xDiaMor1+xDiaMor2>xDiaConIntMor else 0
                            xMorFra = round((rega['kapital'] if xCapPer > rega['kapital'] and rega['kapital'] > 0 else (xCapPer if xCapPer <= rega['kapital'] else 0))*xDiaMor2*(self.tas_im_anual/36525),0)
                            xMorCauPer = xMorCauAnt + xMorFra
                            oCauIntMor = oCauIntMor + xMorFra
                        else:
                            xDiaMor = (self.fecha_focal - rega['fecha']).days
                            xDiaMor = xDiaMor if xDiaMor > xDiaConIntMor else 0
                            xMorCauPer = round((rega['kapital'] if xAboCap > rega['kapital'] and rega['kapital'] > 0 else (xAboCap if xAboCap <= rega['kapital'] else 0))*xDiaMor*(self.tas_im_anual/36525),0)
                            oCauIntMor = oCauIntMor + xMorCauPer 
                    xPrimero = False
                    if xPolSegPer > 0:
                        if xSalPorDis >= xPolSegPer:
                            oAboGasPol = oAboGasPol + xPolSegPer
                            xSalPorDis = xSalPorDis - xPolSegPer
                        else:
                            oAboPolSeg = oAboGasPol + xSalPorDis
                            xSalPorDis = 0
                    xMorCauPer = xMorCauPer if self.for_pag != 'L' else 0
                    if xMorCauPer > 0:
                        if xSalPorDis >= xMorCauPer:
                            oAboIntMor = oAboIntMor + xMorCauPer
                            xSalPorDis = xSalPorDis - xMorCauPer
                            self.int_mor_ya_pag = xMorCauPer+xIntMorDes
                        else:
                            oAboIntMor = oAboIntMor + xSalPorDis 
                            self.int_mor_ya_pag = xSalPorDis+xIntMorDes
                            xSalPorDis = 0
                    if xIntPer > 0 :
                        if xSalPorDis >= xIntPer:
                            oAboIntCor = oAboIntCor + xIntPer
                            xSalPorDis = xSalPorDis - xIntPer
                        else:
                            oAboIntCor = oAboIntCor + xSalPorDis
                            xSalPorDis = 0
                    if xCapPer >= 0 and xFecCauCapNeg < rega['fecha']: 
                        if xSalPorDis >= xCapPer:
                            oAboCap = oAboCap + xCapPer
                            xSalPorDis = xSalPorDis - xCapPer 
                            self.int_mor_ya_pag = 0
                        else:
                            oAboCap = oAboCap + xSalPorDis
                            xSalPorDis = 0
                    else:
                        oAboCap = 0
                        self.int_mor_ya_pag
#  causar la mora total si paga algo pero no queda al dia avanza al siguiente regisdtro 
#   for regb in lista_al_dia[lista_al_dia.index(rega) + 1:]:  error encontrado 20 jul 2025 todo es regb
                for regb in lista_al_dia[lista_al_dia.index(rega):]:
                    xAboCap = xAboCap + regb['kapital'] 
                    xAboIntCor = xAboIntCor + regb['intcor']   
                    xAboIntMor = xAboIntMor + regb['intmor'] 
                    xAboPolSeg = xAboPolSeg + regb['polseg'] 
                    if regb['fecha'] <= xFecUltPag and xAboCap > 0:
                        xDiaMor = (self.fecha_focal - regb['fecha']).days if xFecUltPag > self.fecha_focal else  (self.fecha_focal - xFecUltPag).days
                        xDiaMor = xDiaMor if xDiaMor > xDiaConIntMor else 0
                        oCauIntMor = oCauIntMor + round((regb['kapital'] if xAboCap > regb['kapital'] else xAboCap)*(xDiaMor if xDiaMor > 0 else 0)*(self.tas_im_anual/36525),0)
                    else:
                        xDiaMor = (self.fecha_focal - regb['fecha']).days if (self.fecha_focal - regb['fecha']).days > 0 else 0
                        xDiaMor = xDiaMor if xDiaMor > xDiaConIntMor else 0
                        oCauIntMor = oCauIntMor + round((regb['kapital'] if xAboCap > regb['kapital'] else xAboCap)*xDiaMor*(self.tas_im_anual/36525),0)
                break 
        
#   * aqui sobra dinero y se puede distribuir hacia adelante   
        lista_posterior = [objeto for objeto in self.lista_mov if objeto['fecha'] > self.fecha_focal and objeto['tipmov'] == '1']    
        for reg2 in lista_posterior:
            if xSalPorDis > 0:
                xAboCap = xAboCap + reg2['kapital']
                xAboIntCor = xAboIntCor + reg2['intcor']  
                xAboIntMor = xAboIntMor + reg2['intmor']
                xAboPolSeg = xAboPolSeg + reg2['polseg']
                xPolPer = xAboPolSeg if xAboPolSeg > reg2['polseg'] else reg2['polseg']
                xPolPer = xPolPer if xPolPer > 0 else 0
                xCapPer = xAboCap if xAboCap < reg2['kapital'] else reg2['kapital']
                xCapPer = xCapPer if xCapPer > 0 else 0                    
                xIntPer = xAboIntCor if xAboIntCor < reg2['intcor'] and xAboIntCor >=0 else reg2['intcor'] if  xAboIntCor >= 0 else 0
                xFacInt = ((reg2['fecha'] - self.fecha_focal).days if (reg2['fecha'] - self.fecha_focal).days > 0 else 0)*self.tas_ic_dia
                xConIntAnt = round(xCapPer * self.tas_ic_dia,0) * (reg2['fecha'] - self.fecha_focal).days if (reg2['fecha'] - self.fecha_focal).days > 0 else 0
                xTotPer = xCapPer + xIntPer + xPolPer - xConIntAnt
                if xTotPer <= xSalPorDis and xTotPer >= 0:
                    oAboPolSeg = oAboPolSeg + xPolPer    
                    oAboCap = oAboCap + xCapPer
                    oConIntAnt = oConIntAnt + xConIntAnt
                    oAboIntCor = oAboIntCor + xTotPer-xCapPer-xPolPer
                    xSalPorDis = xSalPorDis - xTotPer
                else:
                    if xSalPorDis > xPolPer:
                        oAboPolSeg = oAboPolSeg + xPolPer
                        xSalPorDis = xSalPorDis - xPolPer
                    else:
                        oAboGasPol = oAboGasPol + xSalPorDis
                        xSalPorDis = 0 
                    xFacInt = round(xFacInt,4)
                    if xSalPorDis > xIntPer:
                        xCap = int((xSalPorDis - xIntPer*(1-xTasDesIntPer/xTasIntPer))/(1-xFacInt*(1-xTasDesIntPer/xTasIntPer)))
                        xConIntAnt = int(xCap*xFacInt)
                        oConIntAnt = oConIntAnt + xConIntAnt
                        oAboIntCor = oAboIntCor + xIntPer - xConIntAnt
                        oAboCap = oAboCap + xSalPorDis - xIntPer + xConIntAnt
                    else:
                        xFraInt=int(xSalPorDis*xTasDesIntPer/xTasIntPer)
                        oAboIntCor = oAboIntCor + xSalPorDis + xFraInt
                    xSalPorDis = 0
                if oAboIntCor+xSalPorDis<=0:
                    break
            else:
                break
        if oAboIntCor + oConIntAnt < 0:
            if oAboIntCor < 0:
                oAboIntCor = oAboIntCor - oAboIntCor
        self.int_mor_cau =  oCauIntMor
        self.capital_a_pag = oAboCap
        self.int_cor_a_pag = oAboIntCor
        self.pol_seg_a_pag = oAboPolSeg
        self.int_mor_a_pag = oAboIntMor
        self.acreedor_a_pag = 0
        self.aju_ic_a_pag = -oConIntAnt
    
    def distri_pago_abo(self,iValorPorDis,idet_pro = None):
        print('distri_pago_abo')
        self.tip_pag = 'ABOCA'
        xFec_mod = None
        if idet_pro != None:
            reg_pag_act = DETALLE_PROD.objects.filter(id = idet_pro).first()
            if reg_pag_act != None:
                xValPagAct = -reg_pag_act.valor
            if xValPagAct != iValorPorDis or xFec_mod != self.fecha_focal or reg_pag_act.concepto == 'ABOCU':
                return 2
            regis = [fila for fila in self.lista_mov if fila['fecha'] == self.fecha_focal and fila['tip_mov'] == '7']
            self.capital_a_pag = regis['kapital']
            self.int_cor_a_pag = regis['intcor']
            self.pol_seg_a_pag = regis['polseg']
            self.int_mor_a_pag = regis['intmor']
            self.acreedor_a_pag = regis['acreed']
            return 1
        xPagoPorDis = iValorPorDis
        self.liq_al_dia(self.fecha_focal)
        xSalCapDia = self.sal_cap_dia
        xSalIntDia = self.sal_int_dia
        xSalMora = self.int_mor_cau
        xSalPolDia = self.sal_ps_dia
        xSalCapTot = self.sal_cap_tot
        xIntCauFra = self.int_cau_fra
        xIntAjuPagAnt = self.int_aju_pa
        xIntPagTot = self.int_pag_tot
        xPagCuoPolAde = 0
        xSalPolDia = xSalPolDia + xPagCuoPolAde
        xIntDia = xSalIntDia if xSalIntDia > 0 else -xIntPagTot if xSalIntDia + xIntPagTot < 0 else xSalIntDia
        xAjuIntAnt = xSalIntDia - xIntDia if xIntDia < 0 else 0
        xIntDia = xIntDia + xIntAjuPagAnt
        xSalMora = xSalMora if self.for_pag == 'P' else 0
        if xPagoPorDis < xSalCapDia+xIntDia + xSalMora + xSalPolDia + xIntCauFra :
            return 3
        xAcre = 0
        print('xIntDia ',xIntDia,'  xIntCauFra ',xIntCauFra)
        xAboCap = xPagoPorDis - (xIntDia + xSalMora +xSalPolDia+xIntCauFra)
        if xAboCap > xSalCapTot:
            xAcre = xAboCap - xSalCapTot
            xAboCap = xSalCapTot
        self.capital_a_pag = xAboCap
        self.int_cor_a_pag = xIntDia + xIntCauFra
        self.pol_seg = xSalPolDia
        self.int_mor_a_pag = xSalMora
        self.acreedor_a_pag = xAcre
        return 0
        
    def distri_pago_condona(self,iValPorDis):
        self.tip_pag = 'CONDO'

        return
    
    def distri_pago_castigo(self,iValPorDis):
        self.tip_pag = 'KASTI'
        return
    
    def aplicar_pago(self,iValPorDis): # aquí hay datos quemados OJO
        Cliente = CLIENTES.objects.filter(codigo='A').first()
        CenCos = CENTROCOSTOS.objects.filter(cliente = Cliente,codigo='A001').first()
        Oficina = OFICINAS.objects.filter(codigo='A0001').first()
        Credito = CREDITOS.objects.filter(oficina=Oficina,cod_cre = self.cod_cre).first()
        ImpConCre = IMP_CON_CRE.objects.filter(id=Credito.imputacion_id).first()
        Socio = ASOCIADOS.objects.filter(id = Credito.socio_id).first()
        Ter = TERCEROS.objects.filter(id = Socio.tercero_id).first()
        if ImpConCre == None:
            print('No Existe Imp Contable')
            return
        xValPag = -(self.capital_a_pag + self.int_cor_a_pag + self.pol_seg_a_pag + self.int_mor_a_pag + self.acreedor_a_pag)
        if xValPag == 0 or xValPag != iValPorDis:
            return
        DocCon = DOCTO_CONTA.objects.filter(oficina=Oficina,per_con = self.fecha_focal.year,codigo=1).first()
        HecEco = HECHO_ECONO.objects.filter(docto_conta=DocCon,numero = 1).first()
        if HecEco == None:
            HecEco = HECHO_ECONO.objects.create(docto_conta=DocCon,numero = None,fecha=self.fecha_focal,descripcion='Aboca Prueba')
        DetPro = DETALLE_PROD.objects.filter(hecho_econo = HecEco,oficina = Oficina,centro_costo = CenCos,producto='CR',concepto = self.tip_pag,subcuenta=self.cod_cre).first()
        if DetPro == None:
            DetPro = DETALLE_PROD.objects.create(hecho_econo = HecEco,oficina = Oficina,centro_costo = CenCos,producto='CR',concepto = self.tip_pag,subcuenta=self.cod_cre,valor = -xValPag)
        if self.capital_a_pag != 0:
            PlaCta = PLAN_CTAS.objects.filter(cliente = Cliente,per_con = DocCon.per_con,cod_cta = ImpConCre.kpte_cap).first()
            DetEco = DETALLE_ECONO.objects.filter(hecho_econo = HecEco,detalle_prod = DetPro,cuenta = PlaCta,tercero = Ter).first()
            if DetEco == None:
                DetEco = DETALLE_ECONO.objects.create(hecho_econo = HecEco,detalle_prod = DetPro,cuenta = PlaCta,tercero = Ter)
            if self.capital_a_pag < 0:
                DetEco.credito = -self.capital_a_pag
                DetEco.debito = 0
                DetEco.valor_1 = 0
                DetEco.valor_2 = -self.capital_a_pag
            else:
                DetEco.credito = -self.capital_a_pag
                DetEco.debito = 0
                DetEco.valor_1 = 0
                DetEco.valor_2 = -self.capital_a_pag
            DetEco.item_concepto = 'kapita'
            DetEco.detalle = self.tip_pag,'  Capital = '+self.cod_cre    
            DetEco.save()
        if self.int_cor_a_pag != 0:
            PlaCta = PLAN_CTAS.objects.filter(cliente = Cliente,per_con = DocCon.per_con,cod_cta = ImpConCre.kpte_ic).first()
            DetEco = DETALLE_ECONO.objects.filter(hecho_econo = HecEco,detalle_prod = DetPro,cuenta = PlaCta,tercero = Ter).first()
            if DetEco == None:
                DetEco = DETALLE_ECONO.objects.create(hecho_econo = HecEco,detalle_prod = DetPro,cuenta = PlaCta,tercero = Ter)
            if self.int_cor_a_pag < 0:
                if self.capital_a_pag < 0:
                    DetEco.credito = -self.int_cor_a_pag
                    DetEco.debito = 0
                    DetEco.valor_1 = 0
                    DetEco.valor_2 = -self.int_cor_a_pag
                else:
                    DetEco.credito = -self.int_cor_a_pag
                    DetEco.debito = 0
                    DetEco.valor_1 = 0
                    DetEco.valor_2 = -self.int_cor_a_pag
                DetEco.detalle = self.tip_pag,'  Int Cor = '+self.cod_cre
                DetEco.item_concepto = 'IntCor'
                DetEco.save()
        if self.int_mor_a_pag != 0:
            PlaCta = PLAN_CTAS.objects.filter(cliente = Cliente,per_con = DocCon.per_con,cod_cta = '41504001').first()
            DetEco = DETALLE_ECONO.objects.filter(hecho_econo = HecEco,detalle_prod = DetPro,cuenta = PlaCta,tercero = Ter).first()
            if DetEco == None:
                DetEco = DETALLE_ECONO.objects.create(hecho_econo = HecEco,detalle_prod = DetPro,cuenta = PlaCta,tercero = Ter)
            if self.int_mor_a_pag < 0:
                if self.int_mor_a_pag < 0:
                    DetEco.credito = -self.int_mor_a_pag
                    DetEco.debito = 0
                    DetEco.valor_1 = 0
                    DetEco.valor_2 = -self.int_mor_a_pag
                else:
                    DetEco.credito = -self.int_mor_a_pag
                    DetEco.debito = 0
                    DetEco.valor_1 = 0
                    DetEco.valor_2 = -self.int_mor_a_pag
                DetEco.item_concepto = 'IntMor'
                DetEco.detalle = self.tip_pag,'  Int Mor = '+self.cod_cre
                DetEco.save()


        if self.int_mor_cau != 0:    #  Faltan mas Condiciones
            CamCre = CAMBIOS_CRE.objects.filter(det_pro = DetPro,tip_cam = '2').first()
            if CamCre == None:
                CamCre = CAMBIOS_CRE.objects.create(det_pro = DetPro,tip_cam = '2')
            CamCre.int_mor = self.int_mor_cau
            CamCre.capital = 0
            CamCre.int_cor = 0
            CamCre.pol_seg = 0
            CamCre.des_pp = 0
            CamCre.fecha = HecEco.fecha
            CamCre.acreedor = 0
            CamCre.save()
        
        params = [0.0,0,0,0.0,0.0,0,0.0,' ',date(1900,1,1),0]
        self.lista_mov = cargue_mov_cre(self.cod_cre,params)
        lista_causa = [objeto for objeto in self.lista_mov if objeto['tipmov'] == '1']    
        for reg in lista_causa:   #  Guarda Causacion por si se elimina el movimiento se puede restaurar 
            RegResCau = CREDITOS_CAUSA.objects.create(cod_cre = self.cod_cre,cuota = reg['cuota'],fecha=reg['fecha'],
                    capital = reg['kapital'],int_cor = reg['intcor'],oficina = Oficina,comprobante = DetPro)   #  Importantisimo si hay comprobante_id es historico
        xTotCap = xTotIC = 0
        xSalCap = self.cap_ini
        lista_al_dia = [objeto for objeto in self.lista_mov if objeto['fecha'] <= self.fecha_focal]
        for reg in lista_al_dia:
            if reg['tipmov'] != 'A':
                # print(reg['tipmov'],'',reg['kapital'],' ',reg['intcor'])
                xTotCap = xTotCap + reg['kapital']
                xTotIC = xTotIC + reg['intcor']
                xSalCap = xSalCap + (reg['kapital'] if reg['kapital'] < 0 else 0)
        lista_final = CREDITOS_CAUSA.objects.filter(Q(comprobante_id=None) & Q(cod_cre=self.cod_cre) &
            Q(oficina=Oficina) & Q(fecha__gte=self.fecha_focal)).order_by('cuota')
        xFecAnt = self.fecha_focal
        xPrimero = True
        xIntIni = 0
        #print('SAL CAP INI ',xSalCap)
        for reg in lista_final:     #  se re aplican causaciones futuras
            # print('FEcHA ',reg.fecha,'  sALCAp ',xSalCap)
            if xSalCap > 0:
                xIntMes = round(xSalCap * self.tas_ic_dia,0) * (reg.fecha - xFecAnt).days 
                if xPrimero and self.tip_pag == 'ABOCU':
                    xCapMes = 0
                    xIntIni = xIntMes
                    xPrimero = False
                else:
                    xCapMes = self.val_cuo - xIntMes - xIntIni
                    xIntIni = 0
                xCapMes = xCapMes if xSalCap - xCapMes > 0 else xSalCap 
                reg.capital = xCapMes - xTotCap
                reg.int_cor = xIntMes - xTotIC
                xSalCap = xSalCap - xCapMes
                xTotCap = 0
                xTotIC = 0
            else:
                reg.capital = 0
                reg.int_cor = 0
            xFecAnt = reg.fecha
            reg.save()
        #print('FECHA FINAL ',xSalCap)
            
    def eliminar_pago(self,iDetPro):
        Oficina = OFICINAS.objects.filter(codigo='A0001').first()
        DetPro = DETALLE_PROD.objects.filter(id = iDetPro).first()
        if DetPro == None:
            return
        if DetPro.concepto == 'ABOCA' or DetPro.concepto == 'ABOCU' or DetPro.concepto == 'CASTI':
            CauCres = CREDITOS_CAUSA.objects.filter(comprobante_id = DetPro,cod_cre=self.cod_cre,oficina=Oficina)
            if CauCres == None:
                return
            CauCreRets = CREDITOS_CAUSA.objects.filter(comprobante_id = None,cod_cre=self.cod_cre,oficina=Oficina)
            for CauCreRet in CauCreRets:
                CauCreRet.delete()
            CauCres = CREDITOS_CAUSA.objects.filter(comprobante_id = DetPro,cod_cre=self.cod_cre,oficina=Oficina)
            for CauCre in CauCres:
                CauCre.comprobante_id = None
                CauCre.save()
        HecEco = HECHO_ECONO.objects.filter(id = DetPro.hecho_econo_id).first()   
        DetEcos = DETALLE_ECONO.objects.filter(hecho_econo = HecEco,detalle_prod = DetPro)
        for DetEco in DetEcos:
            DetEco.delete()
        DetPro.delete()
        CreCau = CAMBIOS_CRE.objects.filter(det_pro_id = iDetPro)
        if CreCau != None:
            CreCau.delete()
        return

    def Exportar_mov(self):
        ruta_excel = "c:/aaa/c"+self.cod_cre+".xlsx"
        df = pd.DataFrame(self.lista_mov)
        writer = pd.ExcelWriter(ruta_excel, engine='xlsxwriter')
        df.to_excel(writer, index=False)
        workbook  = writer.book
        worksheet = writer.sheets['Sheet1']  # Ajusta el nombre de la hoja según tu caso
        workbook.close()
        #for reg in tab_liq :
        #    print(reg['cuota'],'  ',reg['fecha'],'  ',reg['tipmov'],'  ',reg['kapital'],'  ',reg['intcor'],'  ',reg['intmor'])

class Sal_cre:
    def __init__(self, cod_cre,estado,sal_cap_tot,cap_dia,int_dia,sal_mor,dia_mor):
        self.cod_cre = cod_cre
        self.estado = estado
        self.sal_cap_tot = sal_cap_tot
        self.cap_dia = cap_dia
        self.int_dia = int_dia
        self.sal_mor = sal_mor
        self.dia_mor = dia_mor
  
def imprime_liq(liq_cre):
    print('Credito Nro.     ',liq_cre.cod_cre)
    print('kapital Inicial  ',liq_cre.cap_ini)
    print('Fecha Desembolso ',liq_cre.fec_des)
    print('Forma de Pago    ',liq_cre.for_pag)
    print('Tasa Efec. Anual ',liq_cre.tas_ic_ea)
    print('Tasa Int Cor Dia ',liq_cre.tas_ic_dia)
    print('Tasa Int Mor Anu ',liq_cre.tas_im_anual)
    print('Por Descto PP    ',liq_cre.por_des_pp)
    print('Per Ano          ',liq_cre.per_ano)
    print('Tip Pag          ',liq_cre.tip_pag)
    print('------ Liquidacion de Pagosd -------')
    print('Fecha Focal      ',liq_cre.fecha_focal)
    print('Saldo Cap Tot    ',liq_cre.sal_cap_tot)
    print('Saldo Cap Dia    ',liq_cre.sal_cap_dia)
    print('Saldo int Dia    ',liq_cre.sal_int_dia)
    print('Saldo pol seg    ',liq_cre.sal_ps_dia)
    print('Int Mor No Pagado',liq_cre.sal_int_mor+liq_cre.int_mor_cau)
    print('Dias Mora        ',(liq_cre.fecha_focal-liq_cre.fec_al_dia).days)
    print('Int Aju pa       ',liq_cre.int_aju_pa)
    print('Int Pag Tot      ',liq_cre.int_pag_tot)
    print('Altura           ',liq_cre.altura)
    print('Cuotas Pagadas   ',liq_cre.cuo_pag)
    print('Cuotas Pactadas  ',liq_cre.cuo_pac)
    print('Ult Fecha Al Dia ',liq_cre.fec_al_dia)
    print('Fecha Vencimient ',liq_cre.fec_ven)
    print('------ Datos par Aplicar Pagos -------')
    print('(capital_a_pag)  capital a Pagar  ',liq_cre.capital_a_pag)
    print('(int_cor_a_pag)  Int Cor a Pagar  ',liq_cre.int_cor_a_pag)
    print('(pol_seg_a_pag)  Pol Seg a Pagar  ',liq_cre.pol_seg_a_pag)
    print('(int_mor_a_pag)  Int Mor a Pagar  ',liq_cre.int_mor_a_pag)
    print('(acreedor_a_pag) Sobra en el Pago ',liq_cre.acreedor_a_pag)
    print('(aju_cap_a_pag)  aju cap en pago  ',liq_cre.aju_cap_a_pag)
    print('(aju_ic_a_pag)   aju ic en pago   ',liq_cre.aju_ic_a_pag)
    print('(aju_ps_a_pag)   aju PS en pago   ',liq_cre.aju_ps_a_pag)
    print('(int_mor_cau)    Int Mor Cau Pago ',liq_cre.int_mor_cau) 
    print('(aju_im_a_pag)   aju IM a Pagar   ',liq_cre.aju_im_a_pag)
    print('(int_cau_fra)    Int Cau Fra      ',liq_cre.int_cau_fra)
    print('---------------------------------------')
    print('max Valor Cuota  ',liq_cre.max_pag_couta)
    print('min valor aboca  ',liq_cre.min_pag_aboca)
    print('min valor abocu  ',liq_cre.min_pag_abocu)
    print('sig fecha pago1  ',liq_cre.fec_sig_pag1)
    print('sig fecha pago2  ',liq_cre.fec_sig_pag2)
    print('int_mor_ya_pag   ',liq_cre.int_mor_ya_pag)
    
    return

class AsiConRow:
    def __init__(self,CodCre,CodCta,Tipo,ItemConc,Nit,Detalle, Debito, Credito,Aplicado):
        self.cod_cre = CodCre
        self.cod_cta = CodCta
        self.nit = Nit
        self.tipo = Tipo
        self.itemconc = ItemConc
        self.detalle = Detalle
        self.debito = Debito
        self.credito = Credito
        self.aplicado = Aplicado
        
class AsiCon:
    def __init__(self):
        self.rows = []
        self.indexed_rows = {}

    def actualizar(self,CodCre,CodCta,Tipo,ItemConc,Nit,Detalle, Debito, Credito):
        # Crear una clave para buscar en el índice
        clave_busqueda = (CodCre,CodCta,Tipo,ItemConc)
        reg_existe = self.indexed_rows.get(clave_busqueda)
        if reg_existe:
            reg_existe.detalle = reg_existe.detalle + ('' if Detalle in reg_existe.detalle else ';'+Detalle)  
            reg_existe.debito = reg_existe.debito + Debito
            reg_existe.credito = reg_existe.credito + Credito
        else:
            # Crear un nuevo registro si no existe
            nuevo_registro = AsiConRow(CodCre,CodCta,Tipo,ItemConc,Nit,Detalle, Debito, Credito,' ')
            self.rows.append(nuevo_registro)
            self.indexed_rows[clave_busqueda] = nuevo_registro

    def eliminar_iguales(self):
        # Filtrar los registros donde Debito es igual a Credito
        self.rows = [registro for registro in self.rows if registro.Debito != registro.Credito]

    def netear_valores(self):
        nuevos_rows = []
        for registro in self.rows:
            if registro.debito == registro.credito:
                # No se agrega el registro, se elimina al no añadirlo a la nueva lista
                continue
            elif registro.debito > registro.credito:
                registro.debito -= registro.credito
                registro.credito = 0
                nuevos_rows.append(registro)
            else:
                registro.credito -= registro.debito
                registro.debito = 0
                nuevos_rows.append(registro)
        self.rows = nuevos_rows
        
    
    def contabilizar(self,docto,numero,fecha):
        HecEco = HECHO_ECONO.objects.filter(docto_conta = docto,numero = numero).first()
        if HecEco != None:
            DETALLE_ECONO.objects.filter(hecho_econo = HecEco).delete()
            DETALLE_PROD.objects.filter(hecho_econo = HecEco).delete()
        else:
            HecEco = HECHO_ECONO.objects.create(docto_conta = docto,numero = numero)
        HecEco.detalle = 'Reclasificacion de Capital e Intereses del mes y calculo de deterioro'
        HecEco.save()
        for regis in self.rows:
            DetPro = DETALLE_PROD.objects.filter(hecho_econo = HecEco,producto = 'RP',concepto = 'RPKI',subcuenta = regis.cod_cre).first()
            if DetPro == None:
                DetPro = DETALLE_PROD.objects.create(hecho_econo = HecEco,producto = 'RP',concepto = 'RPKI',subcuenta = regis.cod_cre)
            DetPro.oficina = docto.oficina
            DetPro.valor = 0
            DetPro.save()
            Cred = CREDITOS.objects.filter(oficina = docto.oficina,cod_cre = regis.cod_cre).first()
            PlaCue = PLAN_CTAS.objects.filter(cliente = docto.oficina.cliente,per_con = fecha.year,cod_cta=regis.cod_cta).first()
            if PlaCue == None:
                regis.aplicado = 'N'
                continue
            DetEco = DETALLE_ECONO.objects.create(hecho_econo = HecEco,detalle_prod = DetPro,tercero = Cred.socio.tercero,
                cuenta = PlaCue,item_concepto = regis.tipo,
                detalle = 'Cre='+regis.cod_cre+' Tip='+ regis.tipo+' Ite='+regis.itemconc,
                debito = regis.debito,credito = regis.credito)
            DetEco.save()

    def convertir_a_dataframe(self):
        data = {
            'cod_cre': [],
            'cod_cta': [],
            'tipo': [],
            'nit': [],
            'itemconc': [],
            'detalle': [],
            'debito': [],
            'credito': [],
            'aplicado': []
        }

        for row in self.rows:
            data['cod_cre'].append(row.cod_cre)
            data['cod_cta'].append(row.cod_cta)
            data['nit'].append(row.nit)
            data['itemconc'].append(row.itemconc)
            data['tipo'].append(row.tipo)
            data['detalle'].append(row.detalle)
            data['debito'].append(row.debito)
            data['credito'].append(row.credito)
            data['aplicado'].append(row.aplicado)
        df = pd.DataFrame(data)
        return df

    def guardar_en_excel(self, nombre_archivo, ubicacion):
        df = self.convertir_a_dataframe()
        ruta_completa = os.path.join(ubicacion, nombre_archivo)
        df.to_excel(ruta_completa, index=False, engine='openpyxl')
        return ruta_completa  # Devolver la ruta completa del archivo guardado

class CateHistRow:
    def __init__(self,CodCre,FechaRef,Categoria,Valor):
        self.CodCre = CodCre
        self.Categoria = Categoria
        self.FechaRef = FechaRef
        self.Valor = Valor
        
class CateHist:
    def __init__(self):
        self.rows = []
        self.indexed_rows = {}

    def actualizar(self,CodCre,FechaRef,Categoria,Valor):
        # Crear una clave para buscar en el índice
        clave_busqueda = (CodCre,FechaRef)
        registro_existente = self.indexed_rows.get(clave_busqueda)
        if registro_existente:
            registro_existente.CodCre = CodCre
            registro_existente.FechaRef = FechaRef
            registro_existente.Categoria = Categoria
            registro_existente.valor = Valor
        else:
            # Crear un nuevo registro si no existe
            nuevo_registro = CateHistRow(CodCre,FechaRef,Categoria,Valor)
            self.rows.append(nuevo_registro)
            self.indexed_rows[clave_busqueda] = nuevo_registro


class perdida_esperada:
    Oficina = None
    fecha = None
    arr_his = np.zeros(36, dtype=int)

    def __init__(self,iOficina,iFecha):
        self.Oficina = iOficina 
        self.fecha = iFecha

    def obtener_saldos_ctas_aho(fecha_limite, oficina_id):
        sql = """
            SELECT so.cod_aso, ca.num_cta, -SUM(dp.valor) AS saldo
            FROM detalle_prod dp
            INNER JOIN ctas_ahorro ca ON ca.num_cta = dp.subcuenta AND ca.oficina_id = %s
            INNER JOIN asociados so ON so.id = ca.asociado_id
            INNER JOIN hecho_econo he ON he.id = dp.hecho_econo_id AND he.fecha <= %s
            INNER JOIN docto_conta dc ON dc.id = he.docto_conta_id AND dc.oficina_id = %s
            WHERE dp.producto = 'AH'
            GROUP BY so.cod_aso, ca.num_cta
            HAVING saldo > 0
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, [oficina_id, fecha_limite, oficina_id])
            resultados = cursor.fetchall()  # Retorna lista de tuplas (cod_aso, num_cta, saldo)

        return [
            {'cod_aso': row[0], 'num_cta': row[1], 'saldo': row[2]}
            for row in resultados
        ]

    def calculo_z_punt(self,fecha):
        PE_CARTE_HIS.objects.filter(oficina = self.Oficina,fecha = fecha).delete()
        saldos_ctas = self.obtener_saldos_ctas_aho(fecha)
        saldos_indexados = {}
        for item in saldos_ctas:
            cod_aso = item['cod_aso']
            if cod_aso not in saldos_indexados:
                saldos_indexados[cod_aso] = []
            saldos_indexados[cod_aso].append(item) 
        self.arr_his.fill(0) 
        fecha_limite = fecha - timedelta(days=32)  # Restar 32 días
        Creds = CREDITOS.objects.filter(oficina=self.Oficina,fec_des__lte=fecha ).exclude(Q(estado='C') & Q(fec_ult_pag__lt=fecha_limite)
            ).exclude(estado='X').exclude(estado='H')
        #Creds = CREDITOS.objects.filter(oficina=self.Oficina,cod_cre = '128535')
        for Cred in Creds:
            #print('CodCre ',Cred.cod_cre)
            soc = ASOCIADOS.objects.filter(oficina = self.Oficina,id = Cred.socio_id).first()
            xFecIngCoo = soc.fec_afi
            xAgnoIni = xFecIngCoo.year
            xFecNac = soc.fec_nac
            xApoFec = saldo_aporte_socio_fecha(self.Oficina,soc.cod_aso,fecha)
            ter = TERCEROS.objects.filter(cliente = self.Oficina.cliente,id = soc.tercero_id).first()
            xTipDoc =  'C' if ter.tip_ter == 'N' else 'N' if ter.tip_ter == 'J' else ' '
            max_fecha = DETALLE_PROD.objects.filter(hecho_econo__docto_conta__oficina = self.Oficina, producto='CR',subcuenta=Cred.cod_cre
                ).aggregate(max_fecha=Max('hecho_econo__fecha'))['max_fecha']
            max_fecha = Cred.fec_des if max_fecha is None else  max_fecha 
            xCumple_cre = '1' if max_fecha + timedelta(days=180) > fecha else '0'
            xEA =  1 if xCumple_cre == '1' and xApoFec > 0 else 0
            xANTIPRE1 = 1 if (Cred.fec_des - xFecIngCoo).days < 31 else 0 
            xANTIPRE2 = 1 if (Cred.fec_des - xFecIngCoo).days > 365*3 else 0
            xREESTRUCT = 1 if Cred.cod_des == "P" or Cred.cod_des == "R" else 0
            xPLAZOL = 1 if Cred.num_cuo_act > 36 else 0
            xVIN2 = 1 if (self.fecha - Cred.socio.fec_afi).days > 3650 else 0
            xAP = 1 if xApoFec > 0 else 0
            XCOOPCDAT = XCUENAHO = XCDAT = xPER = 0
            cuentas_socio = saldos_indexados.get(Cred.socio.cod_aso, [])
            if cuentas_socio:
                for cuenta in cuentas_socio:
                    if cuenta['num_cta'][:2] == '04' and cuenta['saldo'] > 1:
                        XCOOPCDAT = 1
                        XCDAT = 1
                    elif cuenta['saldo'] > 1:
                        XCUENAHO = 1
            fec_cor = fecha.replace(day=1) - timedelta(days=1)
            for iMes in range(36):
                CreHiss = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = fec_cor,cod_cre = Cred.cod_cre)  # cambio en abril 17 de 2025
                self.arr_his[iMes] = 0
                for CreHis in CreHiss:  
                    if CreHis.dias_mor > self.arr_his[iMes]:
                        self.arr_his[iMes] = CreHis.dias_mor
                fec_cor = fec_cor.replace(day=1) - timedelta(days=1)
            M1 = M2 = M3 = NMORAS1_31_60 = NMORAS3_31_60 = NUMMORTRIN = 0
            for iMes in range(36):
                M3 = self.arr_his[iMes] if self.arr_his[iMes] > M3 else M3
                if iMes < 24: 
                    M2 = self.arr_his[iMes] if self.arr_his[iMes] > M2 else M2
                if iMes < 12: 
                    M1 = self.arr_his[iMes] if self.arr_his[iMes] > M1 else M1

                    if self.arr_his[iMes] >= 31 and self.arr_his[iMes] <= 60:
                        NMORAS1_31_60 = NMORAS1_31_60 + 1
                if iMes < 3: 
                    if self.arr_his[iMes] >= 31 and self.arr_his[iMes] <= 60:
                        NMORAS3_31_60 = NMORAS3_31_60 + 1
            XM3 = XM12 = 0
            for iMes in range(12):
                if self.arr_his[iMes] >= XM3 and iMes < 3:
                    #print('imes ',self.arr_his[iMes])
                    XM3 = self.arr_his[iMes]
                if self.arr_his[iMes] >= XM12:
                    XM12 = self.arr_his[iMes]
            if XM3 >= 16 and XM3 <= 30:
                xMora315 = 1
            else:
                xMora315 = 0
            if XM12 > 60: 
                xMora1260 = 1
            else:
                xMora1260 = 0
            xCodigo = '  '
            if Cred.imputacion.cod_imp == '7' or Cred.imputacion.cod_imp == '9' or Cred.imputacion.cod_imp == 'A' or Cred.imputacion.cod_imp == 'B': 
                if xTipDoc == 'C':
                    xCodigo = '03'
                else:
                    if Cred.for_pag == 'L':
                        xCodigo = '01'
                    else:
                        xCodigo = '02'
            xTC = xFE = xESIN = xFAMOR = xVALCUOTA = xVALPRES = xOCOOP = xFONAHO = xFONDPLAZO = xENTIDAD1 = 0
            HisPun = PE_CARTE_HIS.objects.filter(oficina = self.Oficina,fecha = self.fecha,cod_cre = Cred.cod_cre).first()
            if HisPun == None:
                HisPun = PE_CARTE_HIS.objects.create(oficina = self.Oficina,fecha = self.fecha,cod_cre = Cred.cod_cre)
            HisPun.modalidad = 'CCSL' if Cred.for_pag == 'P' else 'CCCL'
            HisPun.val_ea = xEA
            HisPun.val_fe = xFE
            HisPun.val_valcuota = xVALCUOTA
            HisPun.val_fondplazo = xFONDPLAZO
            HisPun.val_mora315 = xMora315
            HisPun.val_mora1230 = 1 if M1 >= 31 and M1 <= 60 else 0
            HisPun.val_mora1260 = xMora1260
            HisPun.val_mora2430 = 1 if M2 >= 31 and M2 <= 60 and HisPun.val_mora1230 == 0 else 0
            HisPun.val_mora3660 = 1 if M3 > 60 else 0
            HisPun.val_simmora = 1 if M3 < 31 else 0
            Mod = PE_MODE_REFE.objects.filter(cliente = self.Oficina.cliente,modalidad = HisPun.modalidad).first()
            xz = 0
            xz = xz + Mod.constante + HisPun.val_ea*Mod.coe_ea + HisPun.val_fe * Mod.coe_fe + HisPun.val_valcuota*Mod.coe_valcuota 
            xz = xz + HisPun.val_fondplazo*Mod.coe_fondplazo + HisPun.val_mora1230*Mod.coe_mora1230 + HisPun.val_mora1260*Mod.coe_mora1260 
            xz = xz + HisPun.val_mora2430*Mod.coe_mora2430 + HisPun.val_simmora*Mod.coe_sinmora + HisPun.val_mora3660*Mod.coe_mora3660
            xz = xz + HisPun.val_mora315*Mod.coe_mora315
            xPuntaje = 1/(1+math.exp(-xz))
            HisPun.z = xz
            HisPun.puntaje = xPuntaje
            #if HisPun.cod_cre == '74933':
            #    print('Mod.constante ',Mod.constante,'  Mod.coe_ea',Mod.coe_ea,'  Mod.coe_mora1230 ',Mod.coe_mora1230,'  Mod.coe_mora315',Mod.coe_mora315)
            #    print('HisPun.z ',HisPun.z)
            RanCals = PE_CALIF_RANGO.objects.filter(cliente = self.Oficina.cliente,clase_coop = self.Oficina.cliente.clase_coop,
                modalidad = HisPun.modalidad).order_by('-calificacion')
            xCal = ' '
            for RanCal in RanCals:
                if HisPun.puntaje < RanCal.pi_puntaje:
                    xCal = RanCal.calificacion
            HisPun.calificacion = xCal
            PerEsp = PE_PI_CALIF.objects.filter(cliente = self.Oficina.cliente,clase_coop = self.Oficina.cliente.clase_coop,
                modalidad = HisPun.modalidad,calificacion = HisPun.calificacion).first()
            HisPun.pi = PerEsp.pi_porcent
            HisPun.vea = 0
            HisPun.pe = 0 
            HisPun.save()
        return

    def asignar_valores_pe(self,fecha):
        fecha_limite = fecha - timedelta(days=32)  # 
        cre_mess = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = fecha)
        for cre_mes in cre_mess:
            cred = CREDITOS.objects.filter(oficina = self.Oficina,cod_cre = cre_mes.cod_cre).first()
            xTipDoc = 'C' if cred.socio.tercero.tip_ter == 'N' else 'N' if cred.socio.tercero.tip_ter == 'J' else '  '
            mod_pe = PE_CARTE_HIS.objects.filter(oficina = self.Oficina,fecha = fecha,cod_cre = cred.cod_cre).first()  
            if mod_pe == None:
                print('no encontrado ',cred.cod_cre)
                continue
            cre_mes.cat_mod = mod_pe.calificacion
            cre_mes.zeta = mod_pe.z
            cre_mes.puntaje = mod_pe.puntaje
            xmodelo = '    '
            if cre_mes.cod_imp_con == '7' or cre_mes.cod_imp_con == '9' or cre_mes.cod_imp_con == 'A' or cre_mes.cod_imp_con == '8':
                xDiasMorDefault = 121
                if  xTipDoc == 'C':
                    xCodigo = '03'
            else: 
                xDiasMorDefault = 91 
            if cre_mes.for_pag == 'L':
                xCodigo = '01'
                xmodelo = 'CCCL' 
            else:
                xCodigo = '02' 
                xmodelo = 'CCSL'
            xCat_Max = cre_mes.cat_mod
            xcat_sel = 'M'
            if cre_mes.cat_arr > xCat_Max:     
                xcat_sel = 'D'              
                xCat_Max = cre_mes.cat_arr       
            if cre_mes.cat_ree > xCat_Max:
                xcat_sel = 'R'               
                xCat_Max = cre_mes.cat_ree
            if cred.cat_eva > xCat_Max:
                xcat_sel = 'E'	            
                xCat_Max = cred.cat_eva
            cre_mes.cat_sel = xcat_sel
            xPI = -1
            if xmodelo == '    ':
                if xCat_Max == 'A':
                    xPI = 0.0037
                if xCat_Max == 'B':
                    xPI = 0.0621
                if xCat_Max == 'C':
                    xPI = 0.1243
                if xCat_Max == 'D':
                    xPI = 0.2105
                if xCat_Max == 'E': 
                    xPI = 0.5897
                if xCat_Max == 'F':
                    xPI = 1
            else:
                ran_pe = PE_PI_CALIF.objects.filter(cliente_id = 1,clase_coop = 'EAYC',modalidad = xmodelo,
                    calificacion = xCat_Max).first()
                if ran_pe != None:
                    xPI = ran_pe.pi_porcent / 100
                else:
                    xPI = 1
            if cre_mes.dias_mor >= xDiasMorDefault:   
                xPI = 1

            xClaGar = cred.tip_gar
            xPDI = 0  
            if xCodigo != '  ':
                if xClaGar == '1 ':
                    xPDI = 60 
                    if cre_mes.for_pag == 'P':
                        if cre_mes.dias_mor < 31:
                            xPDI = 45
                        else:
                            if cre_mes.dias_mor < 301:
                                xPDI = 60
                            else:
                                if cre_mes.dias_mor < 511:
                                    xPDI = 70
                                else:
                                    xPDI = 100 
                    else:
                        if cre_mes.dias_mor <  91:
                            xPDI = 45
                        else:
                            if cre_mes.dias_mor <  211:
                                xPDI = 60
                            else:
                                if cre_mes.dias_mor <  421:
                                    xPDI = 70
                                else:
                                    xPDI = 100 
                if xClaGar == '2 ':
                    xPDI = 40
                    if cre_mes.dias_mor > 720:
                        xPDI = 100
                    else:
                        if cre_mes.dias_mor > 360:
                            xPDI = 70
                if xClaGar == '15':
                    xPDI = 75
                    if cre_mes.for_pag == 'P':
                        if cre_mes.dias_mor < 31:
                            xPDI = 50
                        else:
                            if cre_mes.dias_mor < 121:
                                xPDI = 75
                            else:
                                if cre_mes.dias_mor < 181:
                                    xPDI = 85
                                else:
                                    xPDI = 100
                    else:
                        if cre_mes.dias_mor < 91:
                            xPDI = 45
                        else:
                            if cre_mes.dias_mor < 121:
                                XPDI = 75
                            else:
                                if cre_mes.dias_mor < 181:
                                    xPDI = 85
                                else:
                                    xPDI = 100
            else:  
                xPDI = 100   

            cre_mes.cla_gar = xClaGar
            cre_mes.pro_inc = xPI
            cre_mes.pdi = xPDI
            cre_mes.vea = -1
            cre_mes.per_esp = -1
            cre_mes.conta_ali = -1
            cre_mes.pro_ind_kap = -1
            cre_mes.pro_ind_int = -1
            cre_mes.categoria = xCat_Max
            cre_mes.cat_sel = xcat_sel
            cre_mes.ali_acu = -1
            cre_mes.save()
        return

    #per_mes.calculo_pi(fecha)


# nit c(12),tip_ter c(1),CAT_ANT C(1),ProKapAnt n(12),ProIntAnt n(12),PeAnt n(12),CAT_ACT C(1),;
#           ProKapAct n(12),ProIntAct n(12),PeAct n(12),ali_conta_ant n(4),cat_arr c(1),ali_acu_ant n(12),gasto_acum n(12),PorKap n(6,2)

def ini_reg_calculo_pe(icod_cre):
    return {
        'cod_cre' : icod_cre,
        'cat_ant' : ' ',
        'nit': '',  # Nit inicial
        'pro_kap_ant': 0,  # Capital inicial
        'pro_int_ant': 0,  # Interés inicial
        'per_esp_ant': 0,  # Interés inicial
        'por_kap':0,
        'cat_act' : ' ',
        'pro_kap_act': 0,  # Capital inicial
        'pro_int_act': 0,  # Interés inicial
        'per_esp_act': 0,  # Interés inicial
        'gasto_acum':0,
    }

class Reclasificacion:
    Oficina = None
    fecha_ant_rec = None
    fecha_rec = None
    CtaOrdDeb = "832100    "
    CtaOrdCre = "88050102  "
    AsiConRPE = AsiCon()
    
    def __init__(self,Oficina,ifecha):
        self.Oficina = Oficina
        self.fecha_rec = ifecha
        self.fecha_ant_rec = ifecha.replace(day=1) - timedelta(days=1)
        self.CtaPteCreCap = '14433501'
        self.CtaPteCreInt = '14433001'
        return
    
    def calculos_base(self):
        Cliente = CLIENTES.objects.filter(codigo='A').first()        
        CreMovKC = CAMBIOS_CRE.objects.filter(tip_cam ='4',fecha__gt=self.fecha_ant_rec, fecha__lte=self.fecha_rec,
            det_pro__hecho_econo__docto_conta__oficina = self.Oficina)
        if CreMovKC != None:
            for reg in CreMovKC:
                DetPro = DETALLE_PROD.objects.filter(id = reg.det_pro_id).first()
                CreHis = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = self.fecha_ant_rec,cod_cre = DetPro.subcuenta).first()
                xCreCas = ' '
                if reg.capital != 0 and reg.int_cor  != 0:
                    xCreCas = 'T'
                elif reg.int_cor != 0:
                    xCreCas = 'K'
                CreHis.castigo = xCreCas
                CreHis.save()
        CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha=self.fecha_rec).delete()   #  se marcan los registros para luego borrarlos si no se reinicio        
        Creditos = CREDITOS.objects.filter(oficina=self.Oficina,fec_des__lte = self.fecha_rec 
            ).exclude(
                # Excluir créditos con estado 'C' y fec_ult_pag < self.fecha_ant_rec
                Q(estado='C') & Q(fec_ult_pag__lt=self.fecha_rec)
            ).exclude(
                # Excluir créditos con estado 'H'
                estado='H'
            ).exclude(
                # Excluir créditos con estado 'H'
                fec_des__gt = self.fecha_rec
            )

        #Creditos = CREDITOS.objects.filter(oficina=self.Oficina)  #  SOLO PARA PROBAR 
        for Credito in Creditos:
            liq_cre = Liquida_cre(Credito.cod_cre,self.fecha_rec) 
            if liq_cre.lista_mov == None:
                Credito.estado = 'H'
                Credito.save()
                continue 
            liq_cre.liq_al_dia(self.fecha_rec)
            #print('liq_cre.sal_cap_tot ',liq_cre.sal_cap_tot)
            if liq_cre.sal_cap_tot <= 0 :
                continue 
            liq_cre.calculo_periodo()
            xdias_mor = (liq_cre.fecha_focal-liq_cre.fec_al_dia).days
            xdias_mor = xdias_mor if xdias_mor > 0 else 0
            if xdias_mor < 1:
                xCat = 'A'
            else:
                # print(' ord(Credito.cod_des)',Credito.cod_des)
                CatDesDia = CAT_DES_DIA_CRE.objects.filter(cliente = self.Oficina.cliente,codigo = ord(Credito.cod_des),
                    minimo_dias__lte=xdias_mor,maximo_dias__gte=xdias_mor).first()
                if CatDesDia == None:
                    xCat = 'F'
                else:
                    xCat = CatDesDia.categoria
        #    lin_cre = LINEAS_CREDITO.objects.filter(id = Credito.cod_lin_cre_id).first()   
            xAporte = 0
            Aportes = DETALLE_PROD.objects.filter(oficina = self.Oficina,producto='AP',hecho_econo__fecha__lte = self.fecha_rec,
                subcuenta = Credito.socio.cod_aso).aggregate(total_apor=Sum('valor'))
            if Aportes['total_apor'] == None:
                xAporte = 0 
            else:
                xAporte = -Aportes['total_apor']
            xCat = xCat if not (Credito.fec_des.year == self.fecha_rec.year and Credito.fec_des.month == self.fecha_rec.month) else 'A'
            CarCatHis = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha=self.fecha_rec,credito = Credito).first()
            if CarCatHis == None:
                CarCatHis = CARTE_CAT_HIS.objects.create(oficina = self.Oficina,fecha=self.fecha_rec,credito = Credito) 
            CarCatHis.nit = Credito.socio.tercero.doc_ide
            CarCatHis.for_pag = Credito.for_pag            
            CarCatHis.cod_cre = Credito.cod_cre
            CarCatHis.cod_lin_cre = chr(Credito.cod_lin_cre.cod_lin_cre)
            CarCatHis.plazo = Credito.num_cuo_act
            CarCatHis.dias_mor = xdias_mor
            CarCatHis.cap_ini = Credito.cap_ini
            CarCatHis.cod_imp_con = Credito.imputacion.cod_imp
            CarCatHis.sal_cap_pe = liq_cre.sal_cap_tot 
            CarCatHis.cat_mor = xCat
            CarCatHis.sal_cap_dia = liq_cre.sal_cap_dia
            CarCatHis.sal_int_dia = liq_cre.sal_int_dia        
            CarCatHis.int_cau_res_per = (liq_cre.int_cau_fra+liq_cre.int_aju_pa) if liq_cre.sal_cap_tot > 0 else 0
            
            CarCatHis.val_gar_hip = Credito.val_gar_hip
            #CarCatHis.conta_ali = (liq_cre.cuo_pac - liq_cre.altura) if liq_cre.cuo_pac - liq_cre.altura else 24
            CarCatHis.int_pag_per = liq_cre.int_pag_per
            CarCatHis.int_conkas_per = liq_cre.int_condo
            CarCatHis.aporte = xAporte
            CarCatHis.save()
        CatPorNit = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = self.fecha_rec).values('nit').annotate(
            sum_cap_ini=Sum('cap_ini'),sum_val_gar_hip=Sum('val_gar_hip'),max_categoria=Max('cat_mor'))
        for row in CatPorNit: 
            sum_cap_tot = row['sum_cap_ini']
            sum_vr_gar_hip = row['sum_val_gar_hip'] or 0
            max_categoria = row['max_categoria']
            CatPorNits = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = self.fecha_rec,nit = row['nit'])   #  recorre por codigo de credito
            xSaldo_1 = xSaldo_2 = 0
            for CatPorNit in CatPorNits:
                if max_categoria == 'A':
                    xSaldo_1 = xSaldo_1 + CatPorNit.sal_cap_pe
                else:
                    xSaldo_2 = xSaldo_2 + CatPorNit.sal_cap_pe
                #xFactor = CatPorNit.cap_ini /sum_cap_tot  estaba mal hasta el 15 de juniode 2025
                xFactor = CatPorNit.cap_ini / sum_cap_tot        
                CatPorNit.cat_arr = max_categoria
                CatPorNit.val_gar_hip = round(sum_vr_gar_hip*xFactor,0)
                CatPorNit.save()
            for CatPorNit in CatPorNits:
                CatPorNit.saldo_1 = xSaldo_1
                CatPorNit.saldo_2 = xSaldo_2
                CatPorNit.save()
            for CarCat in CatPorNits:
                terce = TERCEROS.objects.filter(cliente = self.Oficina.cliente,doc_ide = CarCat.nit).first()
                xTipDoc = 'C' if terce.tip_ter == 'N' else 'J' if terce.tip_ter == 'N' else ' '
                xcat_ree = ' '
                if CarCat.cod_imp_con == '7' or CarCat.cod_imp_con == '9' or CarCat.cod_imp_con == 'A'  or CarCat.cod_imp_con == 'B':
                    xDiasMorDefault = 121
                else: 
                    xDiasMorDefault = 91 
                if CarCat.dias_mor < xDiasMorDefault:
                    xApl_PE = 'S'  
                else:
                    xApl_PE = 'D'
                XSC1 = CarCat.saldo_1
                XSC2 = CarCat.saldo_2

                if CarCat.cat_arr != 'A':   #  ojo  es CarCatNit.categoria o CarCatNit.cat_arr
                    ICCreInt = IMP_CON_CRE_INT.objects.filter(cod_imp = CarCat.cod_imp_con,categoria = CarCat.cat_arr).first()
                    if ICCreInt == None:
                        xTasPro = 100
                    else:
                        xTasPro = ICCreInt.kporcentaje
                    CarCat.aporte = round(CarCat.aporte*CarCat.sal_cap_pe/XSC2,0)
                    if CarCat.dias_mor  <= 547:
                        xPorGarHip = 0.7
                    else:
                        if CarCat.dias_mor< 730:
                            xPorGarHip = 0.5
                        else:
                            if CarCat.dias_mor <= 910:
                                xPorGarHip = 0.3
                            else:
                                if CarCat.dias_mor <= 1905:
                                    xPorGarHip = 0.15
                                else:
                                    xPorGarHip = 0.15 
                    if CarCat.dias_mor > 0 and CarCat.plazo == 1:
                        xPorGarHip = 0
                    xProvision = round((CarCat.sal_cap_pe - (CarCat.val_gar_hip*xPorGarHip))*xTasPro/100,0) 
                    CarCat.pro_ind_kap = xProvision if xProvision > 0 else 0
                    CarCat.val_gar_hip = round(CarCat.val_gar_hip*xPorGarHip,0)
                    CarCat.save()
                else:
                    if XSC2 == 0:
                        CarCat.aporte = round(CarCat.aporte*CarCat.sal_cap_pe/XSC1,0)
                    else:
                        CarCat.aporte = 0
                CarCat.save()

        print('Termina calculos_base')    
        # termina pero queda faltando cat_ree , apl_pe y saber si es con categoria o cat_arr
        return

    def ReclaProv_capital(self,fecha):
        Cliente = CLIENTES.objects.filter(codigo='A').first()
#  aqui se recorre la cat del periodo para calcular reclasificacion del Capital 
        xNitEmpresa = Cliente.doc_ide
        xCtaOrd = '88050101'
        finals = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = fecha)
        inicios = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha =  self.fecha_ant_rec) 
        RPKI.objects.filter(oficina = self.Oficina, fecha = fecha).delete()
        saldo_cp = []
        indexado = {}
        nuevos_reg = []
        for inicio in inicios:              #   
            if inicio.sal_cap_pe > 0:
                xCodCre = inicio.cod_cre
                xNit = inicio.nit
                xCat = inicio.categoria if inicio.categoria < 'F'else 'E'
                if xCat == ' ':
                    continue
                ic_cre = IMP_CON_CRE_INT.objects.filter(cliente_id = 1,cod_imp = inicio.cod_imp_con,categoria = xCat).first()
                xCodCtaCap = ic_cre.kcta_con
                self.AsiConRPE.actualizar(xCodCre,xCodCtaCap,'RK','RecKap',xNit,xCat,0,inicio.sal_cap_pe)
                nuevos_reg.append({
                    'cod_cre': inicio.cod_cre,'nit': xNit,'debito': 0,'credito': inicio.sal_cap_pe,
                    'cap_ini_ini': inicio.cap_ini,'cap_ini_fin': 0
                })

        for final in finals:
            if final.sal_cap_pe > 0:
                xCodCre = final.cod_cre
                xNit = final.nit
                xCat = final.categoria if final.categoria < 'F'else 'E'
                if xCat == ' ':
                    continue
                ic_cre = IMP_CON_CRE_INT.objects.filter(cliente_id = 1,cod_imp = final.cod_imp_con,categoria = xCat).first()
                xCodCtaCap = ic_cre.kcta_con
                self.AsiConRPE.actualizar(xCodCre,xCodCtaCap,'RK','RecKap',xNit,xCat,final.sal_cap_pe,0)
                nuevos_reg.append({
                    'cod_cre': final.cod_cre,'nit': xNit,'debito': final.sal_cap_pe,'credito': 0,
                    'cap_ini_ini': 0,'cap_ini_fin': final.cap_ini
                })

        for nuevo in nuevos_reg:
            codcre = nuevo['cod_cre']
            if codcre in indexado:
                fila = indexado[codcre]
                fila['debito'] += nuevo['debito']
                fila['credito'] += nuevo['credito']
                fila['cap_ini_ini'] += nuevo['cap_ini_ini']
                fila['cap_ini_fin'] += nuevo['cap_ini_fin']
            else:
                saldo_cp.append(nuevo)
                indexado[codcre] = nuevo
        #self.AsiConRPE.netear_valores()
        ic_cre = IMP_CON_CRE.objects.filter(cliente_id = 1).first()
        xCtaPteCreCap = ic_cre.kpte_cap

        for fila in saldo_cp:
            miCre = CREDITOS.objects.filter(oficina = self.Oficina,cod_cre = fila['cod_cre'] ).first()
            saldo = fila['debito'] - fila['credito']
            self.AsiConRPE.actualizar(fila['cod_cre'],xCtaPteCreCap,'RK','RecKap',miCre.socio.tercero.doc_ide,'Rec Kap',-saldo if saldo < 0 else 0,saldo if saldo >= 0 else 0)
        
        for inicio in inicios:
            reg = RPKI.objects.filter(oficina = self.Oficina,fecha = fecha,cod_cre = inicio.cod_cre).first()
            if reg == None:
                reg = RPKI.objects.create(oficina = self.Oficina,fecha = fecha,cod_cre = inicio.cod_cre)
            reg.tipo = '1'
            reg.cod_imp = inicio.cod_imp_con
            reg.int_dia_ini = inicio.sal_int_dia
            reg.nit = inicio.nit
            reg.cat_ini = inicio.categoria
            reg.int_cau_ini = inicio.int_cau_res_per
            reg.sal_cap_ini = inicio.sal_cap_pe
            reg.cre_con_cas = inicio.castigo 
            reg.pro_ind_ini = inicio.pro_ind_kap
            reg.gas_pro_ind_ini = inicio.gas_pro_ind_acu
            reg.gas_gen_ini = inicio.gas_pro_gen
            reg.save()
        
        for final in finals:
            reg = RPKI.objects.filter(oficina = self.Oficina,fecha = fecha,cod_cre = final.cod_cre).first()
            if reg == None :
                reg = RPKI.objects.create(oficina = self.Oficina,fecha = fecha,cod_cre = final.cod_cre)
                reg.tipo = '3'
                reg.cod_imp = final.cod_imp_con
            else:
                reg.tipo = '2'
            reg.int_dia_fin = final.sal_int_dia
            reg.nit = final.nit
            reg.cat_fin = final.categoria
            reg.int_cau_fin = final.int_cau_res_per
            reg.sal_cap_fin = final.sal_cap_pe
            reg.pro_ind_fin = final.pro_ind_kap
            reg.gas_pro_ind_fin = final.gas_pro_ind_acu
            reg.gas_gen_fin = final.gas_pro_gen
            reg.save()
        
        regs = RPKI.objects.filter(oficina = self.Oficina,fecha = fecha)
        for reg in regs:
            xGasProGenFin = reg.gas_gen_ini
            ic_reg = IMP_CON_CRE.objects.filter(cliente_id = 1,cod_imp = reg.cod_imp).first()
            if ic_reg == None:
                print('No Imp ',reg.cod_cre,'TIPO ',reg.tipo)
                continue
            xCtaProGen = ic_reg.kdet_gen
            xCtaProGenAdi = ic_reg.kdet_gen_adi
            xCtaIngGen = ic_reg.kdet_gen_rec
            xCtaGasGen = ic_reg.kdet_gen_gas
            xDifProGen = round(reg.sal_cap_ini*0.01,0) - round(reg.sal_cap_fin*0.01,0)
            xDifProGenAdi = round(reg.sal_cap_ini*0.005,0) - round(reg.sal_cap_fin*0.005,0)
            if reg.tipo > '1':  
                self.AsiConRPE.actualizar(reg.cod_cre,xCtaProGen,'PG','ProGen',reg.nit,'Rec Kap',0,0)     
                if xDifProGen + xDifProGenAdi > 0:
                    self.AsiConRPE.actualizar(reg.cod_cre,xCtaProGen,'PG','ProGen',xNit,'Rec Kap',xDifProGen,0)
                    self.AsiConRPE.actualizar(reg.cod_cre,xCtaProGenAdi,'PG','ProGAd',xNit,'Rec Kap',xDifProGenAdi,0)
                    xCreGas = xDifProGen+xDifProGenAdi if reg.gas_gen_ini > xDifProGen+xDifProGenAdi else reg.gas_gen_ini                     
                    xCreIng = xDifProGen + xDifProGenAdi - xCreGas 
                    xGasProGenFin = xGasProGenFin - xCreGas  
                    if xCreIng > 0:
                        self.AsiConRPE.actualizar(reg.cod_cre,xCtaIngGen,'PG','Proing',xNit,'Rec Kap',0,xCreIng)
                    if xCreGas > 0:
                        self.AsiConRPE.actualizar(reg.cod_cre,xCtaGasGen,'PG','ProGas',xNit,'Rec Kap',0,xCreGas)
                else:
                    self.AsiConRPE.actualizar(reg.cod_cre,xCtaProGen,'PG','ProGen',xNit,'Rec Kap',0,-xDifProGen)
                    self.AsiConRPE.actualizar(reg.cod_cre,xCtaProGenAdi,'PG','ProGAd',xNit,'Rec Kap',0,-xDifProGenAdi)
                    self.AsiConRPE.actualizar(reg.cod_cre,xCtaGasGen,'PG','ProGas',xNit,'Rec Kap',-xDifProGen-xDifProGenAdi,0)
                    xGasProGenFin = xGasProGenFin - xDifProGen - xDifProGenAdi
            else:
                if reg.tipo == '1':
                    self.AsiConRPE.actualizar(reg.cod_cre,xCtaProGen,'PG','ProGen',xNit,'Rec Kap',xDifProGen,0)
                    self.AsiConRPE.actualizar(reg.cod_cre,xCtaProGenAdi,'PG','ProGAd',xNit,'Rec Kap',xDifProGenAdi,0)
                    xIngRec = xDifProGen+xDifProGenAdi
                    if xGasProGenFin > 0:
                        self.AsiConRPE.actualizar(reg.cod_cre,xCtaGasGen,'PG','ProGas',xNit,'Rec Kap',0,xGasProGenFin)
                        xIngRec = xIngRec - xGasProGenFin
                    if xIngRec > 0:
                        self.AsiConRPE.actualizar(reg.cod_cre,xCtaIngGen,'PG','ProIng',xNit,'Rec Kap',0,xIngRec)
                    xGasProGenFin = 0
            carhis = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = fecha,cod_cre = reg.cod_cre).first()
            if carhis != None:
                carhis.gas_pro_gen = xGasProGenFin if fecha.month < 12 else 0
                carhis.save()
            reg.gas_gen_fin = xGasProGenFin
            reg.save()
        
#   abril 12 2025 requerimientos de supersolidaria Cuentas de Oredn Capital
        fec_ini_ord_cap = date(2024,12,31)
        regs = RPKI.objects.filter(oficina = self.Oficina,fecha = fecha)
        for reg in regs:
            xNit = reg.nit
            imp_cap = IMP_CON_CRE.objects.filter(cliente = Cliente,cod_imp = reg.cod_imp).first()
            xcod_mod = imp_cap.cod_mod
            his_ini = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha =  self.fecha_ant_rec,cod_cre = reg.cod_cre).first()
            if his_ini != None:
                xcatini = his_ini.categoria if his_ini.categoria < 'F' else 'E'
                mod_ini = MODALIDADES.objects.filter(cliente = Cliente,cod_mod = xcod_mod,categoria = xcatini).first()
                if mod_ini == None:
                    print('Credito ',reg.cod_cre,'  xcodmod ',xcod_mod,'  categoria ',his_ini.categoria)
                
                if self.fecha_ant_rec == fec_ini_ord_cap:
                    self.AsiConRPE.actualizar(reg.cod_cre,mod_ini.cod_cta,'OK','ProGas',xNit,'CtaOrd',reg.sal_cap_ini,0)
                else:
                    self.AsiConRPE.actualizar(reg.cod_cre,mod_ini.cod_cta,'OK','ProGas',xNit,'CtaOrd',reg.sal_cap_ini,0)

            his_fin = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = fecha,cod_cre = reg.cod_cre).first()
            xdifer = reg.sal_cap_ini - reg.sal_cap_fin
            if his_fin != None:
                xcatfin = his_fin.categoria if his_fin.categoria < 'F' else 'E'
                mod_fin = MODALIDADES.objects.filter(cliente = Cliente,cod_mod = xcod_mod,categoria = xcatfin).first()
            else:
                mod_fin = mod_ini
            if self.fecha_ant_rec == fec_ini_ord_cap:
                if xdifer < 0:
                    self.AsiConRPE.actualizar(reg.cod_cre,mod_fin.cod_cta,'OK','ProGas',xNit,'CtaOrd',-xdifer,0)
                else:
                    self.AsiConRPE.actualizar(reg.cod_cre,mod_fin.cod_cta,'OK','ProGas',xNit,'CtaOrd',0,xdifer)
            else:
                self.AsiConRPE.actualizar(reg.cod_cre,mod_fin.cod_cta,'OK','ProGas',xNit,'CtaOrd',0,reg.sal_cap_fin)
            if self.fecha_ant_rec == fec_ini_ord_cap:
                self.AsiConRPE.actualizar(reg.cod_cre,xCtaOrd,'OK','ProGas',xNit,'CtaOrd',0,reg.sal_cap_fin)
            else:
                if xdifer >= 0:
                    self.AsiConRPE.actualizar(reg.cod_cre,xCtaOrd,'OK','ProGas',xNit,'CtaOrd',0,xdifer)
                else:
                    self.AsiConRPE.actualizar(reg.cod_cre,xCtaOrd,'OK','ProGas',xNit,'CtaOrd',-xdifer,0)
        return 
    
    def ReclaIntCor(self,Oficina):
        print('   Reclasificacion Interes  ',datetime.now())
        otros = CREDITOS.objects.filter(oficina = self.Oficina,fec_des__year = self.fecha_rec.year, fec_des__month = self.fecha_rec.month)
#   For 1  ciCLo Repetitivo para adicionar a  RPKI los Desembolsos de eSe mes
        for otro in otros:
            miRpki = RPKI.objects.filter(oficina = self.Oficina,fecha = self.fecha_rec,cod_cre = otro.cod_cre).first()
            if miRpki == None:
                miRpki = RPKI.objects.create(oficina = self.Oficina,fecha = self.fecha_rec,cod_cre = otro.cod_cre)
                miRpki.tipo = 0
            miRpki.cod_imp = otro.imputacion.cod_imp
            miRpki.sal_cap_ini = otro.cap_ini
            miRpki.nit = otro.socio.tercero.doc_ide
            miRpki.save()

#   For 2  Ciclo repetitivo para cargar el interes corriente Pgado del mes en RPKI;  distribuye El pago en ant act y ade ; iNiciAliza camPos
        CARTERA_CXC.objects.filter(oficina=self.Oficina,fecha=self.fecha_rec).delete()
        CurCatHis = list(CARTERA_CXC.objects.filter(oficina=self.Oficina,fecha=self.fecha_ant_rec).values())
        CateIntes = RPKI.objects.filter(oficina = Oficina,fecha = self.fecha_rec)
        for CateInte in CateIntes:
            CatAct = CARTE_CAT_HIS.objects.filter(oficina = Oficina,fecha = self.fecha_rec,cod_cre = CateInte.cod_cre).first()
            CatAnt = CARTE_CAT_HIS.objects.filter(oficina = Oficina,fecha = self.fecha_ant_rec,cod_cre = CateInte.cod_cre).first()
            if CatAnt != None:
                if CatAnt.sal_cat_int > 0:
                    nuevo_registro = {
                        'fecha': self.fecha_ant_rec,
                        'fec_ref': self.fecha_ant_rec,
                        'cod_cre': CatAnt.cod_cre,
                        'categoria':CatAnt.cat_int_mes,
                        'valor': CatAnt.sal_cat_int,
                        'oficina': self.Oficina.id,  
                    }
                    CurCatHis.append(nuevo_registro)
            resultado = DETALLE_ECONO.objects.filter(hecho_econo__fecha__year = self.fecha_rec.year,hecho_econo__fecha__month = self.fecha_rec.month,
                hecho_econo__docto_conta__oficina_id = self.Oficina.id,detalle_prod__producto = 'CR',detalle_prod__subcuenta = CateInte.cod_cre,
                item_concepto='IntCor',
            ).aggregate(
                total=Sum(
                ExpressionWrapper(F('valor_2') - F('valor_1'),output_field=FloatField())
                )
            )
            CateInte.int_pag = resultado['total'] if resultado['total'] else 0
            CateInte.cat_ini = 'A' if CateInte.cat_ini == ' ' else CateInte.cat_ini
            CateInte.cat_fin = 'A' if CateInte.cat_fin == ' ' else CateInte.cat_fin
            CateInte.int_cau_mes = CateInte.int_dia_fin + CateInte.int_cau_fin + CateInte.int_pag - CateInte.int_dia_ini - CateInte.int_cau_ini
            CateInte.cue_pr_cob_A = CateInte.cue_pr_cob_A = CateInte.cue_pr_cob_C = CateInte.cue_pr_cob_D = CateInte.cue_pr_cob_E = CateInte.cue_pr_cob_F = 0
            CateInte.ingreso = CateInte.cue_por_pag = CateInte.cau_ZET = 0
            CateInte.int_cau_mes = CateInte.int_dia_fin + CateInte.int_cau_fin + CateInte.int_pag - CateInte.int_dia_ini -  CateInte.int_cau_ini    
            xIni = CateInte.int_cau_ini + CateInte.int_dia_ini
            xFin = CateInte.int_cau_fin + CateInte.int_dia_fin
            xIpAnt = 0
            xIpAct = 0
            xIpAde = 0
            xPag = CateInte.int_pag
            if xPag > 0 :
                if xIni > xPag:
                    xIpAnt = xPag
                    xPag = 0
                else:
                    if xIni > 0:
                        xIpAnt = xIni
                        xPag = xPag - xIpAnt
                    else:
                        if xFin <= 0:
                            if CateInte.int_cau_mes + xIni > 0:
                                if xPag >= CateInte.int_cau_mes + xIni :
                                    xIpAct = CateInte.int_cau_mes + xIni
                                    xIpAde = xPag - xIpAct
                                else:
                                    xIpAct = xPag 
                            else:
                                xIpAde = xPag 
                        xPag = 0
                if xPag > 0:
                    if CateInte.int_cau_mes > xPag:
                        xIpAct = xIpAct + xPag
                        xPag = 0
                    else:
                        xIpAct = xIpAct + CateInte.int_cau_mes
                        xPag = xPag - CateInte.int_cau_mes
                if xFin >= 0 :
                    if xFin > xPag:
                        xIpAct = xIpAct + xPag
                        xPag = 0
                    else:
                        if CateInte.sal_cap_fin == 0:
                            xIpAct = xIpAct + xPag
                            xPag = 0
                        else: 
                            xIpAct = xIpAct + xFin
                            xPag = xPag - xFin 
                if xPag > 0:
                    xIpAde = xPag
                    xPag = 0
            CateInte.int_pag_ant = xIpAnt
            CateInte.int_pag_act = xIpAct
            CateInte.int_pag_ade = xIpAde
            CateInte.inicio = xIni
            CateInte.final = xFin
            CateInte.ip_ant_A = 0
            CateInte.ip_ant_B = 0
            CateInte.ip_ant_C = 0
            CateInte.ip_ant_D = 0
            CateInte.ip_ant_E = 0
            CateInte.ip_ant_Z = 0
            CateInte.ip_ant_ZC = 0
            CateInte.ip_ant_ZD = 0
            CateInte.ip_ant_ZE = 0
            CateInte.ip_ant_ZF = 0
            CateInte.save()
               
#   for 3 La rutina Importante de Interes Calula ingreso,  cxc,cxp, galoPa cxc  ---------------------------------------------
        CARTERA_CXC.objects.filter(oficina=Oficina,fecha = self.fecha_rec).delete()
        CateIntes = RPKI.objects.filter(oficina=Oficina,fecha=self.fecha_rec)
        for Reg in CateIntes:
            Reg.ingreso = 0  #  por que prece que esta duplicando
            Reg.cue_por_pag = 0
            xCodCre = Reg.cod_cre
            CatAct = CARTE_CAT_HIS.objects.filter(oficina = Oficina,fecha = self.fecha_rec,cod_cre = Reg.cod_cre).first()
            xFin = Reg.final
            xIni = Reg.inicio
            xNit = Reg.nit
            xTipo = 0
            zDebito = 0
            zCredito = 0
            xCatFin = Reg.cat_fin if Reg.cat_fin < 'F' else 'E' 
            if Reg.cat_fin == 'W':
                xCatFin = 'C'
            elif Reg.cat_fin == 'X':
                xCatFin = 'D'
            elif Reg.cat_fin == 'Z':
                xCatFin = 'Z'
            if xIni >= 0 and xFin >=0 and xIni < xFin:      #  comienza debiendo termina debiendo (+)
                xTipo=1
            elif xIni >= 0 and xFin >= 0 and xIni >= xFin:  #   comienza debiendo termina debiendo (-)
                xTipo=2            
            elif xIni < 0 and xFin >= 0:                    #   comienza con saldo a favor termina debiendo
                xTipo = 3
            elif xIni >=0 and xFin < 0:                     #   comienza debiendo termina con saldo a favor
                xTipo = 6
            elif xIni < 0 and xFin < 0 and xFin >= xIni: 	#   comienza con saldo a favor termina con saldo a favor (-)
                xTipo = 7
            elif xIni < 0 and  xFin < 0 and xFin < xIni:    #   comienza con saldo a favor termina con saldo a favor (+)
                xTipo = 8
            ImpCon = IMP_CON_CRE.objects.filter(cliente = Oficina.cliente,cod_imp = Reg.cod_imp).first()
            if ImpCon == None:
                print('Grave  ',Reg.cod_cre,'  Inicio ',Reg.cod_imp,' Final ',Reg.cod_imp)
            ImpConCat = IMP_CON_CRE_INT.objects.filter(cliente = Oficina.cliente,cod_imp = Reg.cod_imp,categoria = xCatFin ).first()
            if Reg.cat_fin < 'G':
                xCtaIntCxC = ImpConCat.cta_int
            else:
                xCtaIntCxC = ImpConCat.cta_ord_int
            #print('xtipo ',xTipo ,' Categoria ',Reg.cat_fin,'  xIni ',xIni,'  xFin',xFin,'  difer ',zDebito-zCredito )
            if Reg.cat_fin < 'C':                           #   Los Interese causados van a ingreso
                self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kcta_ingreso,'RI','ingres',xNit,'ingreso '+Reg.cod_cre,0,Reg.int_cau_mes)
                zCredito = zCredito + Reg.int_cau_mes
                Reg.ingreso = Reg.ingreso - Reg.int_cau_mes
                xDifMes = Reg.int_cau_mes - Reg.int_pag_act - (-xIni if xTipo == 3 else (-xIni if xTipo > 6 else 0))
                xDifMes = xDifMes - (Reg.int_pag if Reg.int_pag < 0 and xTipo == 3 else 0)
                if xDifMes > 0:
                    self.AsiConRPE.actualizar(Reg.cod_cre,xCtaIntCxC,'RI','CxC',xNit,'CxC '+Reg.cod_cre,xDifMes,0)
                    zDebito = zDebito + xDifMes
                    if CatAct != None: 
                        CatAct.cat_int_mes = Reg.cat_fin
                        CatAct.sal_cat_int = xDifMes
                        CatAct.save()
            else:   #  No se afecta el ingreso 
                if xIni < 0 :
                    xIngCre = Reg.int_pag_act - xIni + (xFin if xFin < 0 else 0)
                else:
                    xIngCre = Reg.int_pag_act
                if xIngCre > 0:
                    Reg.ingreso = Reg.ingreso -xIngCre
                    if Reg.cod_cre == '124606':
                        print('Ingreso ',Reg.ingreso )
                    self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kcta_ingreso,'RI','ingres',xNit,'ingreso '+Reg.cod_cre,0,xIngCre)
                    zCredito = zCredito + xIngCre   #    xc+CateInte.IPAct
                #print('Reg.int_cau_mes  ',Reg.int_cau_mes,'  difer ',zDebito-zCredito )
                if Reg.int_cau_mes > xIngCre:
                    self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kic_orden_i,'RI','OrdenI',xNit,'OrdenI '+Reg.cod_cre,0,Reg.int_cau_mes-xIngCre)
                    if Reg.cat_fin == 'C':
                        xCatOrd = 'W'
                    elif Reg.cat_fin == 'D':
                        xCatOrd = 'X'
                    elif Reg.cat_fin == 'E' or Reg.cat_fin == 'F':
                        xCatOrd = 'Z'
                    self.AsiConRPE.actualizar(Reg.cod_cre,ImpConCat.cta_ord_int,'RI','OrdenE',xNit,'OrdenE '+Reg.cod_cre,Reg.int_cau_mes-xIngCre,0)
                    zCredito = zCredito + Reg.int_cau_mes - xIngCre
                    zDebito = zDebito + Reg.int_cau_mes - xIngCre

                    if Reg.int_cau_mes - xIngCre > 0 :
                        if CatAct != None:
                            CatAct.cat_int_mes = xCatOrd
                            CatAct.sal_cat_int =  Reg.int_cau_mes - xIngCre
                            CatAct.save()
                    #  Termina lo que se debe hacer cuando el credito > 'B'
            #print('Reg.int_pag  ',Reg.int_pag,'  difer ',zDebito-zCredito)
            if Reg.int_pag > 0:     #  Aqui Afecta la Cta Pte
                self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kpte_ic,'RI','CtaPte',xNit,'CodCre '+Reg.cod_cre,Reg.int_pag,0)
                zDebito = zDebito + Reg.int_pag
            else:                   #  Pudo haber sido un pago negativo cuando es Interes Adelantado
                self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kpte_ic,'RI','CtaPte',xNit,'CodCre '+Reg.cod_cre,0,-Reg.int_pag)
                zCredito = zCredito - Reg.int_pag
        
#       para xtipo   < 3 or xTipo == 6           
            if xTipo < 3 or xTipo == 6:
                if Reg.int_pag_ant > 0 or (xTipo == 2 and Reg.ingreso > 0):
                    xLimCxC = Reg.int_pag_ant
                    xIntPag = xLimCxC
                    if xTipo == 2 and Reg.ingreso > 0:
                        xLimCxC = xLimCxC + Reg.ingreso

                    #print('xLimCxC  ',xLimCxC ,'  difer ',zDebito-zCredito)

#   for 3.1    Aqui Galopa CurCatHis  solo para el credito actual
                    RegHiss = [regis for regis in  CurCatHis if regis['cod_cre'] == Reg.cod_cre]
                    for RegHis in RegHiss:
                        if RegHis['valor'] > 0: 
                            xAboCxC = RegHis['valor'] if RegHis['valor'] <= xLimCxC else xLimCxC
                            if xAboCxC > 0:
                                xAboIntPag = xIntPag if xAboCxC > xIntPag else xAboCxC
                                xIntPag = xIntPag - xAboIntPag
                                if RegHis['categoria'] < 'G':
                                    xCtaHis = RegHis['categoria']  if RegHis['categoria']  < 'F' else 'E'    
                                else:
                                    if RegHis['categoria']  == 'W':
                                        xCtaHis = 'C'
                                    elif RegHis['categoria']  == 'X':
                                        xCtaHis = 'D'
                                    if RegHis['categoria']  == 'Y' or RegHis['categoria']  == 'Z':
                                        xCtaHis = 'E'
                                RegImpCatH = IMP_CON_CRE_INT.objects.filter(cliente = Oficina.cliente,cod_imp = ImpCon.cod_imp,categoria = xCtaHis).first()
                                if RegHis['categoria']  < 'G':  #  acredita  interes
                                    self.AsiConRPE.actualizar(Reg.cod_cre,RegImpCatH.cta_int,'RI','CxC',xNit,'',0,xAboCxC)
                                    zCredito = zCredito +xAboCxC
                                    if RegHis['categoria']  == 'A':
                                        Reg.ip_ant_A = Reg.ip_ant_A + xAboIntPag
                                    elif RegHis['categoria']  == 'B':
                                        Reg.ip_ant_B = Reg.ip_ant_B + xAboIntPag
                                    elif RegHis['categoria']  == 'C':
                                        Reg.ip_ant_C = Reg.ip_ant_C + xAboIntPag
                                    elif RegHis['categoria']  == 'D':
                                        Reg.ip_ant_D = Reg.ip_ant_D + xAboIntPag
                                    elif RegHis['categoria']  == 'E':
                                        Reg.ip_ant_E = Reg.ip_ant_E + xAboIntPag
                                    elif RegHis['categoria']  == 'F':
                                        Reg.ip_ant_E = Reg.ip_ant_E + xAboIntPag  
                                else:   #  hay recuperacion de Ingreso
                                    self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kcta_ingreso,'RI','IngRec',xNit,'',0,xAboCxC)
                                    self.AsiConRPE.actualizar(Reg.cod_cre,RegImpCatH.cta_ord_int,'RI','OrdenE',xNit,'',0,xAboCxC)
                                    self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kic_orden_i,'RI','OrdenI',xNit,'',xAboCxC,0)
                                    Reg.ingreso = Reg.ingreso - xAboCxC
                                    if Reg.cod_cre == '124606':
                                        print('Ingreso3 ',Reg.ingreso )
                                    if RegHis['categoria']  == 'W':
                                        Reg.ip_ant_ZC = Reg.ip_ant_ZC + xAboCxC
                                    elif RegHis['categoria']  == 'X':
                                        Reg.ip_ant_ZD = Reg.ip_ant_ZD + xAboCxC
                                    elif RegHis['categoria']  == 'Y':
                                        Reg.ip_ant_ZE = Reg.ip_ant_ZE + xAboCxC
                                    elif RegHis['categoria']  == 'Z':
                                        Reg.ip_ant_ZF = Reg.ip_ant_ZF + xAboCxC
                                    zCredito = zCredito + xAboCxC
                                
                                xLimCxC = xLimCxC - xAboCxC
                                RegHis['valor'] = RegHis['valor'] - xAboCxC
                                if RegHis['valor']  > 0 and Reg.int_con > 0:
                                    xOtrVal = Reg.int_con if RegHis['valor'] < Reg.int_con else Reg.int_con
                                    RegHis['valor'] = RegHis['valor'] - xOtrVal
                                    Reg.int_con = Reg.int_con - xOtrVal
                    if xLimCxC > 0:
                        self.AsiConRPE.actualizar(Reg.cod_cre,'51109501','RI','Error',xNit,'Error',0,xLimCxC)
                        zCredito = zCredito + xLimCxC
                        print('Credito ',Reg.cod_cre,'Difer ', xLimCxC)
        
                if xTipo == 6:
                    self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kic_cxp,'RI','CxP',xNit,'CodCre'+Reg.cod_cre,0,Reg.int_pag_ade)
                    zCredito=zCredito + Reg.int_pag_ade
                    Reg.cue_por_pag = Reg.cue_por_pag - Reg.int_pag_ade

#       para xtipo  = 3            
            if xTipo == 3:
                self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kic_cxp,'RI','CxP',xNit,'CodCre'+Reg.cod_cre,-xIni,0)
                Reg.cue_por_pag = Reg.cue_por_pag - xIni
                zDebito = zDebito - xIni

#       para xtipo  == 7 or xTipo == 8: 
            if xTipo == 7 or xTipo == 8:
                xDifDef = xFin - xIni
                if xDifDef > 0:
                    self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kic_cxp,'RI','CxP',xNit,'CodCre'+Reg.cod_cre,xDifDef,0)
                    zCredito = zCredito - xDifDef
                    Reg.cue_por_pag = Reg.cue_por_pag + xDifDef
                else:
                    self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kic_cxp,'RI','CxP',xNit,'CodCre'+Reg.cod_cre,0,-xDifDef)
                    zDebito = zDebito + xDifDef
                    Reg.cue_por_pag = Reg.cue_por_pag + xDifDef

#   for 3.2    ciclo repeTitivO que actuAliza hostorico de cxc inTere  Actualiza las cuentas CxC por nueva Categoria del Credito   
            #print(' F ',zDebito - zCredito)                
            RegHiss = [regis for regis in  CurCatHis if regis['cod_cre'] == Reg.cod_cre]
            for RegHis in RegHiss:
                xNueCat = Reg.cat_fin
                if RegHis['valor'] > 0:
                    if RegHis['categoria'] != xNueCat and  RegHis['categoria'] <= 'F':
                        ImpConCat1 = IMP_CON_CRE_INT.objects.filter(cliente = Oficina.cliente,cod_imp = ImpCon.cod_imp,categoria = RegHis['categoria']).first()
                        self.AsiConRPE.actualizar(Reg.cod_cre,ImpConCat1.cta_int,'RI','CtaInt',xNit,'',0,RegHis['valor'])
                        zCredito = zCredito + RegHis['valor']
                        ImpConCat2 = IMP_CON_CRE_INT.objects.filter(cliente = Oficina.cliente,cod_imp = ImpCon.cod_imp,categoria = xNueCat).first()
                        self.AsiConRPE.actualizar(Reg.cod_cre,ImpConCat2.cta_int,'RI','CtaInt',xNit,'',RegHis['valor'],0)
                        zDebito = zDebito + RegHis['valor']
                        RegHis['categoria'] = xNueCat
                    if (RegHis['categoria'] > 'F') or ((RegHis['categoria']  == 'W' and xNueCat != 'C') or (RegHis['categoria']  == 'X' and xNueCat != 'D')
                        or (RegHis['categoria']  == 'Y' and xNueCat != 'E') or (RegHis['categoria']  == 'Z' and xNueCat != 'F')                               )  : 
            #    and ((RegHis.categoria == "W" and xNueCat != "C") or (RegHis['categoria'] == "X" and xNueCat != 'D') or (RegHis['categoria'] == 'Y' and xNueCat != 'E') or (RegHis['categoria'] == 'Z' and xNueCat != 'F')):
                        if RegHis['categoria'] == 'W':
                            xCtaHom = 'C'
                        elif RegHis['categoria'] == 'X':
                            xCtaHom = 'D'
                        elif RegHis['categoria'] == 'Y':
                            xCtaHom = 'E'
                        elif RegHis['categoria'] == 'Z':
                            xCtaHom = 'F'
                        ImpConCat1 = IMP_CON_CRE_INT.objects.filter(cliente = Oficina.cliente,cod_imp = ImpCon.cod_imp,categoria = xCtaHom).first()
                        self.AsiConRPE.actualizar(Reg.cod_cre,ImpConCat1.cta_ord_int,'RI','CtaOrd',xNit,'',0,RegHis['valor'])                  
                        zCredito = zCredito + RegHis['valor']                       
                        if xNueCat < 'C':
                            Reg.ingreso = Reg.ingreso - RegHis['valor']
                            if Reg.cod_cre == '124606':
                                print('Ingreso4',Reg.ingreso )
                            self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kic_orden_i,'RI','CtaOrdI',xNit,'',RegHis['valor'],0)
                            zDebito = zDebito + RegHis['valor']
                            self.AsiConRPE.actualizar(Reg.cod_cre,ImpCon.kic_rec_int,'RI','RecInt',xNit,'',0,RegHis['valor'])
                            zCredito = zCredito + RegHis['valor']
                            ImpConCat1 = IMP_CON_CRE_INT.objects.filter(cliente = Oficina.cliente,cod_imp = ImpCon.cod_imp,categoria = xNueCat).first()
                            self.AsiConRPE.actualizar(Reg.cod_cre,ImpConCat1.cta_int,'RI','CxC',xNit,xCodCre,RegHis['valor'],0)
                            zDebito = zDebito + RegHis['valor']
                            xNueCatSal  = xNueCat
                        else:
                            if xNueCat == 'C':
                                xNueCatSal = 'W'
                            elif xNueCat == 'D':
                                xNueCatSal = 'X'
                            elif xNueCat == 'E':
                                xNueCatSal = 'Y'
                            elif xNueCat == 'F':
                                xNueCatSal = 'Z'
                            ImpConCat1 = IMP_CON_CRE_INT.objects.filter(cliente = Oficina.cliente,cod_imp = ImpCon.cod_imp,categoria = xNueCat).first()
                            self.AsiConRPE.actualizar(Reg.cod_cre,ImpConCat1.cta_ord_int,'RI','CtaOrd',xNit,xCodCre,RegHis['valor'],0)
                            zDebito = zDebito + RegHis['valor']
                        RegHis['categoria'] = xNueCatSal
            
            if zDebito != zCredito :    #   SELECT RPKIIF zDebito<>zCredito
                if zDebito > zCredito:
                    self.AsiConRPE.actualizar(Reg.cod_cre,'51109501','RI','Error ',xNit,xCodCre,0,zDebito - zCredito)
                else:
                    self.AsiConRPE.actualizar(Reg.cod_cre,'51109501','RI','Error ',xNit,xCodCre,-zDebito+zCredito,0)
            Reg.save()
#   termina la rutina Mas impoRtante  ---------------------------------------------------             
            
#   for 4    Aqui empieza a recorrer  ---------------------------------------------------  
        RegHiss = [regis for regis in  CurCatHis ]
        for RegHis in RegHiss:
            if RegHis['valor'] > 0:
                CatHisCre = CARTERA_CXC.objects.filter(oficina = Oficina,cod_cre = RegHis['cod_cre'],
                    fecha = self.fecha_rec,fec_ref = RegHis['fec_ref'] ,categoria = RegHis['categoria']).first() 
                if CatHisCre == None:
                    CatHisCre = CARTERA_CXC.objects.create(oficina = Oficina,cod_cre = RegHis['cod_cre'],
                    fecha = self.fecha_rec,fec_ref = RegHis['fec_ref'],categoria = RegHis['categoria'])
                CatHisCre.valor = RegHis['valor']
                CatHisCre.categoria = RegHis['categoria']
                CatHisCre.save()
                if RegHis['categoria'] == 'A' :
                    Reg.cue_pr_cob_A = Reg.cue_pr_cob_A + RegHis['valor']
                elif RegHis['categoria'] == 'B' :
                    Reg.cue_pr_cob_B = Reg.cue_pr_cob_B + RegHis['valor']
                elif RegHis['categoria'] == 'C' :
                    Reg.cue_pr_cob_C = Reg.cue_pr_cob_C + RegHis['valor']
                elif RegHis['categoria'] == 'D' :
                    Reg.cue_pr_cob_D = Reg.cue_pr_cob_D + RegHis['valor']
                elif RegHis['categoria'] == 'E' :
                    Reg.cue_pr_cob_E = Reg.cue_pr_cob_E + RegHis['valor']
                elif RegHis['categoria'] == 'F' :
                    Reg.cue_pr_cob_F = Reg.cue_pr_cob_F + RegHis['valor']
                elif RegHis['categoria'] == 'W' :
                    Reg.cau_ZC = Reg.cau_ZC + RegHis['valor']
                elif RegHis['categoria'] == 'X' :
                    Reg.cau_ZD = Reg.cau_ZD + RegHis['valor']
                elif RegHis['categoria'] == 'Y' :
                    Reg.cau_ZE = Reg.cau_ZE + RegHis['valor']
                elif RegHis['categoria'] == 'Z' :
                    Reg.cau_ZET = Reg.cau_ZET + RegHis['valor']
            Reg.save()

#   for 5    Aqui empieza a recorrer  ---------------------------------------------------  
        for CatHis in CurCatHis:
            if CatHis['valor'] and CatHis['categoria'] != ' ':
                CatNue = CARTERA_CXC.objects.filter(oficina = self.Oficina,cod_cre = CatHis['cod_cre'] ,fecha = self.fecha_rec,fec_ref = CatHis['fec_ref']).first()
                if CatNue == None:
                    CatNue = CARTERA_CXC.objects.create(oficina = self.Oficina,cod_cre = CatHis['cod_cre'] ,fecha = self.fecha_rec,fec_ref = CatHis['fec_ref'])
                CatNue.categoria = CatHis['categoria']
                CatNue.valor = CatHis['valor']
                miRpki = RPKI.objects.filter(oficina=Oficina,fecha=self.fecha_rec,cod_cre = CatHis['cod_cre']).first()
                if CatNue.categoria == 'A':
                    miRpki.cue_pr_cob_A = miRpki.cue_pr_cob_A + CatNue.valor
                elif CatNue.categoria == 'B':
                    miRpki.cue_pr_cob_B = miRpki.cue_pr_cob_B + CatNue.valor
                elif CatNue.categoria == 'C':
                    miRpki.cue_pr_cob_C = miRpki.cue_pr_cob_C + CatNue.valor
                elif CatNue.categoria == 'D':
                    miRpki.cue_pr_cob_D = miRpki.cue_pr_cob_D + CatNue.valor
                elif CatNue.categoria == 'E':
                    miRpki.cue_pr_cob_E = miRpki.cue_pr_cob_E + CatNue.valor
                elif CatNue.categoria == 'F':
                    miRpki.cue_pr_cob_F = miRpki.cue_pr_cob_F + CatNue.valor
                elif CatNue.categoria == 'W':
                    miRpki.cau_ZC = miRpki.cau_ZC + CatNue.valor
                elif CatNue.categoria == 'X':
                    miRpki.cau_ZD = miRpki.cau_ZD + CatNue.valor
                elif CatNue.categoria == 'Y':
                    miRpki.cau_ZE = miRpki.cau_ZE + CatNue.valor
                elif CatNue.categoria == 'Z':
                    miRpki.cau_ZF = miRpki.cau_ZF + CatNue.valor
                miRpki.save()

#   for 6    Aqui empieza a recorrer  ---------------------------------------------------           
        misRPKI = RPKI.objects.filter(oficina=Oficina,fecha=self.fecha_rec)
        for miRPKI in misRPKI:
            miCarHis = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = self.fecha_rec,cod_cre = miRPKI.cod_cre).first()
            if miCarHis == None:
                continue
            if miCarHis.cat_int_mes == 'A':
                miRpki.cue_pr_cob_A = miRpki.cue_pr_cob_A + miCarHis.sal_cat_int
            elif miCarHis.cat_int_mes == 'B':
                miRpki.cue_pr_cob_B = miRpki.cue_pr_cob_B + miCarHis.sal_cat_int
            elif miCarHis.cat_int_mes == 'C':
                miRpki.cue_pr_cob_C = miRpki.cue_pr_cob_C + miCarHis.sal_cat_int
            elif miCarHis.cat_int_mes == 'D':
                miRpki.cue_pr_cob_D = miRpki.cue_pr_cob_D + miCarHis.sal_cat_int
            elif miCarHis.cat_int_mes == 'E':
                miRpki.cue_pr_cob_E = miRpki.cue_pr_cob_E + miCarHis.sal_cat_int
            elif miCarHis.cat_int_mes == 'F':
                miRpki.cue_pr_cob_F = miRpki.cue_pr_cob_F + miCarHis.sal_cat_int
            elif miCarHis.cat_int_mes == 'W':
                miRpki.cau_ZC = miRpki.cau_ZC + miCarHis.sal_cat_int
            elif miCarHis.cat_int_mes == 'X':
                miRpki.cau_ZC = miRpki.cau_ZC + miCarHis.sal_cat_int
            elif miCarHis.cat_int_mes == 'Y':
                miRpki.cau_ZD = miRpki.cau_ZD + miCarHis.sal_cat_int
            elif miCarHis.cat_int_mes == 'Z':
                miRpki.cau_ZE = miRpki.cau_ZE + miCarHis.sal_cat_int
            miRpki.save()

#   termina la rutina Mas impoRtante  --------------------------------------------------- 
        RPKI.objects.filter(fecha = self.fecha_rec).update(
            inicio=F('int_cau_ini') + F('int_dia_ini'),
            final=F('int_cau_fin') + F('int_dia_fin')
        )

        # Faltaria lo de Consoli
        # Faltaria lo de creditos reestructurados
        return

    def calculos_pe(self,Oficina):
        calculo_pe = {}
        CarHitAnts = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = self.fecha_ant_rec)
        for CarAnt in CarHitAnts:
            xCatAnt = ' '
            if CarAnt.cat_sel == 'D':
                xCatAnt = CarAnt.cat_arr
            elif CarAnt.cat_sel == 'R':
                xCatAnt = CarAnt.cat_ree
            elif CarAnt.cat_sel == 'E':
                xCatAnt = CarAnt.cat_eva
            elif CarAnt.cat_sel == 'R':
                xCatAnt = CarAnt.cat_ree
            xCatAnt = CarAnt.categoria if xCatAnt == ' ' else xCatAnt
            xCodCre = CarAnt.cod_cre
            if xCodCre not in calculo_pe:
                calculo_pe[xCodCre] = ini_reg_calculo_pe(xCodCre)
                calculo_pe[xCodCre]['nit'] = CarAnt.nit
                calculo_pe[xCodCre]['cat_ant'] = CarAnt.categoria if CarAnt.categoria != ' ' else 'A'
                calculo_pe[xCodCre]['pro_kap_ant'] = CarAnt.pro_ind_kap
                calculo_pe[xCodCre]['pro_int_ant'] = CarAnt.pro_ind_int
                calculo_pe[xCodCre]['per_esp_ant'] = CarAnt.per_esp
                calculo_pe[xCodCre]['gasto_acum'] = CarAnt.gas_pro_ind_acu
                calculo_pe[xCodCre]['por_kap'] = 100
            
        CarHitActs = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = self.fecha_rec)
        for CarAct in CarHitActs:
            xCodCre = CarAct.cod_cre
            if xCodCre == '136619':
                xSalIntCorPE = 0    
            xSalIntCorPE = 0
            xSalIntConTin = 0
            if CarAct.cat_int_mes < 'G':
                xSalIntCorPE =  xSalIntCorPE + CarAct.sal_cat_int
            else:
                xSalIntConTin = xSalIntConTin + CarAct.int_cor_per
            HisCxCs = CARTERA_CXC.objects.filter(oficina = self.Oficina,fecha = self.fecha_rec,cod_cre = xCodCre)
            for HisCxC in HisCxCs:
                if HisCxC.categoria < 'G':
                    xSalIntCorPE =  xSalIntCorPE + HisCxC.valor
                else:
                    xSalIntConTin = xSalIntConTin + HisCxC.valor
            xVea = CarAct.sal_cap_pe + xSalIntCorPE - CarAct.aporte if CarAct.sal_cap_pe + xSalIntCorPE - CarAct.aporte > 0 else 0
            xPE = round(CarAct.pro_inc*CarAct.pdi/100*xVea)
            CarAct.sal_int_pe = xSalIntCorPE 
            CarAct.per_esp = xPE
            CarAct.vea = xVea
            CarAct.sal_int_contin = xSalIntConTin
            CarAct.save()
            if xSalIntCorPE > 0:
                xPorKap = round(CarAct.sal_cap_pe/(CarAct.sal_cap_pe+xSalIntCorPE)*100,2)
            else:
                xPorKap = 100
            if xCodCre not in calculo_pe:
                calculo_pe[xCodCre] = ini_reg_calculo_pe(xCodCre)
                calculo_pe[xCodCre]['nit'] = CarAct.nit
            calculo_pe[xCodCre]['cat_act'] = CarAct.categoria if CarAct.categoria != ' ' else 'A'
            calculo_pe[xCodCre]['pro_kap_act'] = CarAct.pro_ind_kap
            calculo_pe[xCodCre]['pro_int_act'] = CarAct.pro_ind_int
            calculo_pe[xCodCre]['por_kap'] = xPorKap
            calculo_pe[xCodCre]['per_esp_act'] = xPE

        for xcod_cre,per_esp in calculo_pe.items():
        #per_esp = calculo_pe.get('43405')
        #if per_esp:
            if xcod_cre == '137452':
                print('Inicia vaLIDACION')
            xcod_cre =  per_esp['cod_cre']
            xgas_acum = per_esp['gasto_acum'] 
            miRpki = RPKI.objects.filter(oficina = self.Oficina, fecha = self.fecha_rec,cod_cre = xcod_cre).first()
            ImpCon = IMP_CON_CRE.objects.filter(cliente = self.Oficina.cliente,cod_imp = miRpki.cod_imp).first()
            xCtaIngInd = ImpCon.kdet_ind_rec
            xCtaGasInd = ImpCon.kdet_ind_gas
            xCatAnt = per_esp['cat_ant'] if per_esp['cat_ant'] < 'F' else 'A' if per_esp['cat_ant'] ==' ' else 'E'
            ImpConCat = IMP_CON_CRE_INT.objects.filter(cliente = self.Oficina.cliente,cod_imp = miRpki.cod_imp,categoria = xCatAnt).first()
            if ImpConCat == None:
                ImpConCat = IMP_CON_CRE_INT.objects.filter(cliente = self.Oficina.cliente,cod_imp = miRpki.cod_imp,categoria = 'A').first()
            xCtaProIndIni = ImpConCat.cta_pro_ind_cap
            xCtaProIntAnt = ImpConCat.cta_pro_ind_int
            xCatAct = per_esp['cat_act'] if per_esp['cat_act'] < 'F' else 'A' if per_esp['cat_ant'] ==' ' else 'E'
            ImpConCat = IMP_CON_CRE_INT.objects.filter(cliente = self.Oficina.cliente,cod_imp = miRpki.cod_imp,categoria = xCatAct).first()
            if ImpConCat == None:
                ImpConCat = IMP_CON_CRE_INT.objects.filter(cliente = self.Oficina.cliente,cod_imp = miRpki.cod_imp,categoria = 'A').first()
            xCtaProIndFin = ImpConCat.cta_pro_ind_cap
            xCtaProIntAct = ImpConCat.cta_pro_ind_int
            xProKapAct =  round(per_esp['per_esp_act']*per_esp['por_kap']/100,0)
            xProIntAct = per_esp['per_esp_act'] - xProKapAct
            per_esp['pro_kap_act'] = xProKapAct
            per_esp['pro_int_act'] = xProIntAct
            xDifProKap = xProKapAct - per_esp['pro_kap_ant']
            xDifProInt = xProIntAct - per_esp['pro_int_ant'] 
            if per_esp['pro_kap_ant'] > 0:
                self.AsiConRPE.actualizar(xcod_cre,xCtaProIndIni,'PE','PIKap',per_esp['nit'],'cod_Cre='+xcod_cre,per_esp['pro_kap_ant'],0)
            if per_esp['pro_kap_act'] > 0:
                self.AsiConRPE.actualizar(xcod_cre,xCtaProIndFin,'PE','PIKap',per_esp['nit'],'cod_Cre='+xcod_cre,0,per_esp['pro_kap_act'])
            if per_esp['pro_int_ant'] > 0:
                self.AsiConRPE.actualizar(xcod_cre,xCtaProIntAnt,'PE','PIKap',per_esp['nit'],'cod_Cre='+xcod_cre,per_esp['pro_int_ant'],0)
            if per_esp['pro_int_act'] > 0:
                self.AsiConRPE.actualizar(xcod_cre, xCtaProIntAct ,'PE','PIKap',per_esp['nit'],'cod_Cre='+xcod_cre,0,per_esp['pro_int_act'])
            if xDifProKap + xDifProInt > 0:
                self.AsiConRPE.actualizar(xcod_cre,xCtaGasInd,'PE','ProGas',per_esp['nit'],'cod_Cre='+xcod_cre,xDifProKap + xDifProInt ,0)
            else:
                xProRecPer = -(xDifProKap+xDifProInt)
                if per_esp['gasto_acum'] > xProRecPer:
                    self.AsiConRPE.actualizar(xcod_cre,xCtaGasInd,'PE','ProGas',per_esp['nit'],'cod_Cre='+xcod_cre,0,xProRecPer)
                    xgas_acum = xgas_acum - xProRecPer
                else:
                    if xgas_acum > 0:
                        self.AsiConRPE.actualizar(xcod_cre,xCtaGasInd,'PE','ProGas',per_esp['nit'],'cod_Cre='+xcod_cre,0,xgas_acum)
                        xProRecPer = xProRecPer - xgas_acum
                        xgas_acum = 0
                    if xProRecPer > 0:
                        self.AsiConRPE.actualizar(xcod_cre,xCtaIngInd,'PE','RecPro',per_esp['nit'],'cod_Cre='+xcod_cre,0,xProRecPer)
            CreHis = CARTE_CAT_HIS.objects.filter(oficina = self.Oficina,fecha = self.fecha_rec ,cod_cre = xCodCre).first()
            if  CreHis != None:
                CreHis.pro_ind_kap = xProKapAct
                CreHis.pro_ind_int = xProIntAct
                CreHis.gas_pro_ind_acu = xgas_acum 
        return

    def Llevar_a_historico(self,Oficina):
        Creditos = CREDITOS.objects.filter(oficina = Oficina)
        for Credito in Creditos:
            print(Credito.cod_cre)
            if Credito.fec_des.year == self.fecha_rec.year and Credito.fec_des.month == self.fecha_rec.month:
                continue
            HisAnt = CARTE_CAT_HIS.objects.filter(oficina = Oficina,fecha = self.fecha_ant_rec,cod_cre = Credito.cod_cre).first()
            if HisAnt == None:
                Credito.estado = 'H'
                Credito.save()
        return

# --- Uso ejemplo ---

from aportes_app.views import saldo_aporte_socio_fecha
from django.db import connection


def PE_Recla():   
    fecha = date(2025,4,30)   
    print('Inicia Recla_kap_int_PE   ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    pe_mes = perdida_esperada(Oficina,fecha)
    #print('Inicia calculo_z_punt     ',datetime.now())
    #pe_mes.calculo_z_punt(fecha)
    rec_mes = Reclasificacion(Oficina,fecha)
    print('Inicia calculos base      ',datetime.now())
    rec_mes.calculos_base()
    print('Inicia asignar valores pe ',datetime.now())
    pe_mes.asignar_valores_pe(fecha)
    print('Inicia  ReclaProv_capital ',datetime.now())
    rec_mes.ReclaProv_capital(fecha)
    print('Inicia  ReclaIntCor       ',datetime.now())
    rec_mes.ReclaIntCor(Oficina)
    print('Inicia calculos PE        ',datetime.now())
    rec_mes.calculos_pe(Oficina)
    print('Inicia Contabilizar       ',datetime.now())
    rec_mes.AsiConRPE.netear_valores()
    docto = DOCTO_CONTA.objects.filter(oficina = Oficina,per_con = fecha.year,codigo = 34).first()
    numero = fecha.month
    rec_mes.AsiConRPE.contabilizar(docto,numero,fecha)
    rec_mes.AsiConRPE.guardar_en_excel('rkipe_01.xlsx','c:/aaa/')
    print('Final Recla_kap_int_PE    ',datetime.now())
    
def ValLiqCre(): 
    print('Inicio  ',datetime.now())
    lista_creditos = []
    # Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    Creditos = CREDITOS.objects.filter(oficina=Oficina,cod_cre = '129251')
    fecha = date(2025,8,24)
    for Credito in Creditos:
        liq_cre = Liquida_cre(Credito.cod_cre,fecha) 
        #liq_cre.Exportar_mov()
        #liq_cre.eliminar_pago(483603)
        #liq_cre.liq_al_dia()
        if liq_cre.lista_mov == None:
            print('Problemas Credito ',Credito.cod_cre)
            continue
        liq_cre.liq_al_dia()
        sal_cre = Sal_cre(liq_cre.cod_cre,Credito.estado,liq_cre.sal_cap_tot,liq_cre.sal_cap_dia,liq_cre.sal_int_dia,liq_cre.int_mor_cau,(liq_cre.fecha_focal-liq_cre.fec_al_dia).days)
        imprime_liq(liq_cre)
        lista_creditos.append(vars(sal_cre))
        #print('Por Cuota  ',liq_cre.sal_cap_dia+liq_cre.sal_int_dia+liq_cre.int_mor_cau)
        liq_cre.distri_pago_abo(1098437)
        #liq_cre.distri_pago_abo(3000000) 
        #liq_cre.tip_pag = 'ABOCU'
        #print('liq_cre fecha focal 3  ---> ',liq_cre.fecha_focal)
        #print('liq_cre.distri_pago_abo ',liq_cre.distri_pago_abo(579736))
        imprime_liq(liq_cre)

        #   liq_cre.Exportar_mov()
        #   liq_cre.liq_por_cuotas(liq_cre.cuo_pag+2)
        # liq_cre.distri_pago_abo(1078037)
    
    ruta_excel = "c:/aaa/cart_justo.xlsx"
    df = pd.DataFrame(lista_creditos)
    #writer = pd.ExcelWriter(ruta_excel, engine='xlsxwriter')
    #workbook  = writer.book
    #worksheet = writer.sheets['Hoja1']  # Ajusta el nombre de la hoja según tu caso
    #workbook.close()

    #with pd.ExcelWriter(ruta_excel, engine='xlsxwriter') as writer:
    #    df.to_excel(writer, sheet_name='Hoja1', index=False)
    #    workbook = writer.book

    print('Final   ',datetime.now())

#PE_Recla()
#ValLiqCre()
