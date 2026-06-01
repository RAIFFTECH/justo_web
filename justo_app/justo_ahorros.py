from datetime import datetime, timedelta
import math, csv, django, os
import numpy as np
from io import BytesIO
from decimal import Decimal, ROUND_DOWN
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from operator import itemgetter
from django.db.models.functions import Coalesce
from django.db.models import Max, Q, F, Sum, Case, When, Value, FloatField, CharField, IntegerField
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Justo_proy.settings')
django.setup()
from django.core.mail import EmailMessage
from django.conf import settings
import smtplib
from email.mime.text import MIMEText

from terceros_app.models import TERCEROS
from oficinas_app.models import OFICINAS
from documentos_app.models import DOCTO_CONTA
from hecho_economico_app.models import HECHO_ECONO
from ctas_ahorros_app.models import CTAS_AHORRO, INT_DIA_AHO
from detalle_producto_app.models import DETALLE_PROD
from detalle_economico_app.models import DETALLE_ECONO
from lineas_ahorro_app.models import LINEAS_AHORRO
from tasas_lin_aho_app.models import TAS_LIN_AHO
from retefuente_ahorros_app.models import RET_FUE_AHO
from contabilizacion_lineas_ahorros_app.models import IMP_CON_LIN_AHO
from cuentas_app.models import PLAN_CTAS
from ampliacion_cdat_app.models import CTA_CDAT_AMP
from cdat_app.models import CTA_CDAT
from liquidacion_cdat_app.models import CTA_CDAT_LIQ

def es_ultimo_dia_del_mes(fecha):
    siguiente_dia = fecha + timedelta(days=1)
    return siguiente_dia.month != fecha.month

def ultimo_dia_mes_anterior(fecha):
    primer_dia_mes_actual = fecha.replace(day=1)
    ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
    return ultimo_dia_mes_anterior

def obtener_saldos_ctas_ahorros(oficina_id,fecha,subcuenta=None):
    queryset = (
        DETALLE_PROD.objects
        .filter(
            producto='AH',
            hecho_econo__fecha__lt=fecha,
            hecho_econo__docto_conta__oficina_id=oficina_id
        )
        .values('subcuenta')  # Agrupación por subcuenta
        .annotate(total_valor=Sum('valor') * -1)  # Aplica SUM() y niega el resultado
    )
    resultado_dict = {
        item['subcuenta']: {
            'num_cta': item['subcuenta'],
            'total_valor': item['total_valor']
        }
        for item in queryset
    }
    if subcuenta and subcuenta in resultado_dict:
        return {subcuenta: resultado_dict[subcuenta]}
    return resultado_dict

def liquidar_int_diario_y_cdat(fecha):
    mensajes = []
    print('Inicial ',datetime.now(),'   Fecha ',fecha)
    ant_fecha = fecha.replace(day=1) - relativedelta(days=1)

    docto1 = DOCTO_CONTA.objects.filter(oficina_id = 1,per_con = ant_fecha.year,codigo = 13).first()
    com_cie_mes = HECHO_ECONO.objects.filter(docto_conta = docto1,numero = ant_fecha.month).first()
    #if com_cie_mes == None:
    #    mensajes.append('No se Generado el Comprobante de liquidacion del Mes Anterior')
    #    mensajes.append('! Atencion ! Liquidacion del Dia No Exitosa')
    #    return mensajes

    mensajes.append('Liquidacion Interes de la fecha '+ fecha.strftime('%d/%m/%Y') )
    oficina_id = 1
    INT_DIA_AHO.objects.filter(oficina_id=oficina_id, fecha=fecha).update(
        int_dia=0, ret_fue=0, aplicado=' ')
    ret_fue_dia = RET_FUE_AHO.objects.filter(fecha_inicial__lte=fecha, fecha_final__gte=fecha)
    if ret_fue_dia == None:
        mensajes.append('No se encuentran registros de rete_fuente a la Fecha')
        mensajes.append('! Atencion ! Liquidacion del Dia No Exitosa')
        return mensajes
    tas_lin_aho = TAS_LIN_AHO.objects.filter(fecha_inicial__lte=fecha, fecha_final__gte=fecha)
    if not tas_lin_aho.exists():
        mensajes.append('No se encuentran registros de tasas de Interes de la Fecha')
        mensajes.append('! Atencion ! Liquidacion del Dia No Exitosa')
        return mensajes 
    print('tas_lin_aho  ',tas_lin_aho)
    docto = DOCTO_CONTA.objects.filter(oficina_id = 1,per_con = fecha.year,codigo = 131).first()
    comprob = HECHO_ECONO.objects.filter(docto_conta = docto,numero = fecha.timetuple().tm_yday).first()
    if comprob != None:
        print('compRobante elimiNado ')
        DETALLE_ECONO.objects.filter(hecho_econo = comprob).delete()
        DETALLE_PROD.objects.filter(hecho_econo = comprob).delete()
#   Primero se Calcula el Interes Diario    
    saldos_ctas = obtener_saldos_ctas_ahorros(oficina_id,fecha)
    NumLiqDia = 0
    NumLiqCdat = 0
    ValIntDia = 0
    ValIntCdat = 0
    ValRet = 0
    for key, value in saldos_ctas.items():
        if value['total_valor'] > 0 :
            cta_aho = CTAS_AHORRO.objects.filter(oficina_id = oficina_id,num_cta = value['num_cta']).first()
            if cta_aho.lin_aho.per_liq_int == 'D' and cta_aho.num_cta[:2] != '04':
                tas_int_cta = tas_lin_aho.filter(lin_aho_id = cta_aho.lin_aho_id).first() 
                xTasIntDia= tas_int_cta.tiae /100
                xTasNomDia = math.pow(1 + xTasIntDia, 1/365) - 1
                xIntDia = round(value['total_valor']*xTasNomDia,0)
                if xIntDia == 0:
                    continue 
                ret_cta_int = ret_fue_dia.filter(lin_aho = cta_aho.lin_aho).first()
                xRetFueDia = 0
                if xIntDia >= ret_cta_int.bas_liq_int:
                    xRetFueDia = round(xIntDia*ret_cta_int.tas_liq_rf/100,0)
                reg_int_dia = INT_DIA_AHO.objects.filter(oficina_id=oficina_id,
                    num_cta = value['num_cta'],dia_mes = fecha.day).first()
                if reg_int_dia == None:
                    reg_int_dia = INT_DIA_AHO.objects.create(oficina_id=oficina_id,num_cta = value['num_cta'],
                        dia_mes = fecha.day,cta_aho = cta_aho)
                reg_int_dia.fecha = fecha
                reg_int_dia.int_dia = xIntDia
                reg_int_dia.ret_fue = xRetFueDia
                reg_int_dia.cta_aho = cta_aho
                reg_int_dia.aplicado = "N"
                reg_int_dia.save()
                NumLiqDia = NumLiqDia + 1
                ValIntDia = ValIntDia + reg_int_dia.int_dia
                ValRet = ValRet + reg_int_dia.ret_fue
            else:
                if cta_aho.num_cta[:2] == '04':
                    cta_cdat_vence = CTA_CDAT_AMP.objects.filter(cta_aho = cta_aho,fecha = fecha).first()
                    if cta_cdat_vence == None:
                        continue
                    #print('Hay Cdat ',cta_aho.num_cta)
                    cta_cdat = CTA_CDAT.objects.filter(id = cta_cdat_vence.cta_amp_id).first()
                    if cta_cdat == None:
                        print('Pero se sale')
                        continue
                    cta_cdat0 = CTA_CDAT.objects.filter(cta_aho = cta_aho,ampliacion = 0).first()
                    cta_aho1 = CTAS_AHORRO.objects.filter(oficina_id = oficina_id,num_cta = cta_cdat0.cta_int_ret).first()
                    
                    ip_cta_aho = IMP_CON_LIN_AHO.objects.filter(cod_imp = cta_aho1.cod_imp,linea_ahorro_id = cta_aho1.lin_aho_id).first()
                    lin_aho1 = LINEAS_AHORRO.objects.filter(cliente_id = 1,cod_lin_aho = cta_aho.num_cta[:2]).first()
                    xPlaMes = cta_cdat.plazo_mes          
                    xFecIni = cta_cdat.fecha
                    xInt = 0
                    xRetFue = 0
                    xRetFueNue = 0
                    xPer = cta_cdat0.Periodicidad
                    cdats_liq = CTA_CDAT_LIQ.objects.filter(cta_amp_id = cta_cdat_vence.id)
                    for cdat_liq in cdats_liq:
                        #print('Fecha ',cdat_liq.fecha,'  ',cdat_liq.val_int)
                        if cdat_liq.fecha >= fecha:
                            continue
                        xInt = xInt + cdat_liq.val_int
                        xRetFue = xRetFue + cdat_liq.val_ret + cdat_liq.val_ret_nue
                        xRetFueNue = xRetFueNue + cdat_liq.val_ret_nue
                        xFecIni = cdat_liq.fecha
                    xIntPorApl = cta_cdat_vence.valor - xInt
                    ret_fue = ret_fue_dia.filter(lin_aho = cta_aho.lin_aho).first()
                    xRetFuePorApl = 0          
                    xUltRetFue = xIntPorApl * ret_fue.tas_liq_rf if xRetFueNue>0 else 0
                    docto = DOCTO_CONTA.objects.filter(oficina_id = 1,per_con = fecha.year,codigo = 131).first()
                    comprob = HECHO_ECONO.objects.filter(docto_conta = docto,numero = fecha.timetuple().tm_yday).first()
                    if comprob == None:
                        comprob = HECHO_ECONO.objects.create(docto_conta = docto,numero = fecha.timetuple().tm_yday,fecha=fecha,
                            descripcion = 'Liquidacionde Intereses Diarios Cdats ',anulado = 'N',protegido = 'N')
                    comprob.save()
                    if  (cta_cdat_vence.valor > ret_fue.bas_liq_int *30*xPlaMes/xPer) or (xRetFueNue > 0):
    #   caMbios del 24 de Mayo 
                        xRetFuePorApl = round(xIntPorApl*ret_fue.tas_liq_rf/100,0)  
                    if xIntPorApl > 0:
                        print('ip_cta_aho.ctaafeint ',ip_cta_aho.ctaafeint)
                        cta_con_int = PLAN_CTAS.objects.filter(per_con = docto.per_con,cod_cta = ip_cta_aho.ctaafeint).first()
                        if cta_con_int == None:
                            mensajes.append('No existe Cuenta Contable Para Cdat '+cta_aho.num_cta) 
                            mensajes.append('! Atencion ! Liquidacion del Dia No Exitosa')
                            return mensajes
                        det_eco = DETALLE_ECONO.objects.filter(hecho_econo = comprob,cuenta = cta_con_int,tercero = cta_aho.asociado.tercero).first()
                        if det_eco == None:
                            det_eco = DETALLE_ECONO.objects.create(hecho_econo = comprob,cuenta = cta_con_int,tercero = cta_aho.asociado.tercero,
                                debito=0,credito=0)
                        det_eco.detalle = 'Gasto Int Cdat '+cta_aho.num_cta
                        det_eco.debito = det_eco.debito + xIntPorApl
                        det_eco.save()
                        cta_con_cxp = PLAN_CTAS.objects.filter(per_con = docto.per_con,cod_cta = lin_aho1.cta_por_pas).first()
                        det_eco = DETALLE_ECONO.objects.filter(hecho_econo = comprob,cuenta = cta_con_cxp,tercero = cta_aho.asociado.tercero).first()                        
                        if det_eco == None:
                            det_eco = DETALLE_ECONO.objects.create(hecho_econo = comprob,cuenta = cta_con_cxp,tercero = cta_aho.asociado.tercero,
                                debito = 0,credito = 0)
                        det_eco.detalle = 'CxP Int Cdat '+cta_aho.num_cta
                        det_eco.credito = det_eco.credito + xIntPorApl-xRetFuePorApl
                        det_eco.save()
                        if xRetFuePorApl > 0:
                            cta_con_rf = PLAN_CTAS.objects.filter(per_con = docto.per_con,cod_cta = ip_cta_aho.ctaretfue).first()  
                            det_eco = DETALLE_ECONO.objects.filter(hecho_econo = comprob,cuenta = cta_con_rf,
                                tercero = cta_aho.asociado.tercero).first()
                            if det_eco == None:
                                det_eco = DETALLE_ECONO.objects.create(hecho_econo = comprob,cuenta = cta_con_rf,
                                    tercero = cta_aho.asociado.tercero,debito = 0,credito = 0)
                            det_eco.detalle = 'Ret Cdat '+cta_aho.num_cta
                            det_eco.credito = det_eco.credito + xRetFuePorApl
                            det_eco.save()
                    
                    if cta_aho.est_cta == 'A':
                        xCtaCtaAho = ip_cta_aho.ctaafeact 
                    else:
                        cta_aho.est_cta = ip_cta_aho.ctaafeina
                    cta_con_aho = PLAN_CTAS.objects.filter(per_con = docto.per_con,cod_cta = xCtaCtaAho).first()
                    det_pro = DETALLE_PROD.objects.create(hecho_econo = comprob,producto = 'AH',concepto = 'IntCdat',subcuenta=cta_aho1.num_cta)
                    det_pro.valor = -cta_cdat_vence.valor
                    det_pro.save()
                    det_eco = DETALLE_ECONO.objects.create(hecho_econo = comprob,detalle_prod=det_pro,cuenta = cta_con_aho,
                        tercero = cta_aho.asociado.tercero)
                    det_eco.item_concepto = 'IntCda'
                    det_eco.detalle = 'Intereses Abonados A la cuenta '+cta_aho1.num_cta+' por el Cdat '+cta_aho.num_cta
                    det_eco.credito = cta_cdat_vence.valor
                    det_eco.save()
                    if xRetFue + xRetFuePorApl > 0:
                        det_pro = DETALLE_PROD.objects.filter(hecho_econo = comprob,producto = 'AH',concepto = 'IntCdat',subcuenta=cta_aho1.num_cta).first()
                        if det_pro == None:
                            det_pro = DETALLE_PROD.objects.create(hecho_econo = comprob,producto = 'AH',concepto = 'IntCdat',subcuenta=cta_aho1.num_cta)
                        det_pro.valor = xRetFue+xRetFuePorApl


                        det_pro.save()
                        det_eco = DETALLE_ECONO.objects.create(hecho_econo = comprob,detalle_prod=det_pro,cuenta = cta_con_aho,
                            tercero = cta_aho.asociado.tercero)
                        det_eco.item_concepto = 'RFCdat'
                        det_eco.detalle = 'Ret Fue Abonados A la cuenta '+cta_aho1.num_cta+' por el Cdat '+cta_aho.num_cta
                        det_eco.debito = xRetFue + xRetFuePorApl
                        det_eco.save()
                    det_eco = DETALLE_ECONO.objects.filter(hecho_econo = comprob,cuenta = cta_con_cxp,tercero = cta_aho.asociado.tercero).first()                        
                    if det_eco == None:
                        det_eco = DETALLE_ECONO.objects.create(hecho_econo = comprob,cuenta = cta_con_cxp,tercero = cta_aho.asociado.tercero,
                            debito = 0,credito = 0)
                    det_eco.detalle = 'CxP Int Cdat '+cta_aho.num_cta
                    det_eco.debito = det_eco.debito + cta_cdat_vence.valor - xRetFue - xRetFuePorApl
                    det_eco.save()

                    cdat_liq = CTA_CDAT_LIQ.objects.filter(cta_aho = cta_aho,cta_amp_id = cta_cdat_vence.id,tip_liq = 'C').first()
                    #print('Cta Vence ',cta_cdat_vence.id)
                    if cdat_liq == None:
                        cdat_liq = CTA_CDAT_LIQ.objects.create(cta_aho = cta_aho,cta_amp_id = cta_cdat_vence.id,tip_liq = 'C')
                    cdat_liq.fecha = fecha
                    cdat_liq.val_int = xIntPorApl
                    cdat_liq.val_ret = xRetFuePorApl
                    cdat_liq.val_ret_nue = xRetFuePorApl-xUltRetFue if xUltRetFue > 0 else 0
                    cdat_liq.save()
                    cdat_liq = CTA_CDAT_LIQ.objects.filter(cta_aho = cta_aho,cta_amp_id = cta_cdat_vence.id,tip_liq = 'P').first()
                    if cdat_liq == None:
                        cdat_liq = CTA_CDAT_LIQ.objects.create(cta_aho = cta_aho,cta_amp_id = cta_cdat_vence.id,tip_liq = 'P')
                    cdat_liq.fecha = fecha
                    cdat_liq.val_int = -cta_cdat_vence.valor
                    cdat_liq.val_ret = -(xRetFue + xRetFuePorApl)
                    cdat_liq.val_ret_nue = 0
                    cdat_liq.save()
                    cta_cdat_vence.cta_aho_afe = cta_aho1.num_cta
                    cta_cdat_vence.docto = comprob
                    cta_cdat_vence.aplicado = 'S'
                    cta_cdat_vence.save()
                    NumLiqCdat = NumLiqCdat + 1
                    ValIntCdat = ValIntCdat + xIntPorApl 
                    ValRet = ValRet + xRetFuePorApl
                    mensajes.append('Pago de Intereses del Cdat '+cta_aho.num_cta)

    #num_cta = '03-004776'  # Número de, cuenta que deseas consultar
    #saldo = saldos_ctas.get(num_cta, {}).get('total_valor', 'Cuenta no encontrada')
    print('Final   ',datetime.now())
    mensajes.append(f'Cuentas Diarias Liquidadas: {NumLiqDia:,}, Valor de Intereses: {round(ValIntDia,0):,}')
    mensajes.append(f'Cuentas Diarias Liquidadas: {NumLiqCdat:,}, Valor de Intereses: {round(ValIntCdat,0):,}')
    mensajes.append(f'Valor de la Retencion Liq.: {round(ValRet,0):,}')
    mensajes.append('Liquidacion de Interes de Ahorros diaria Realizada con Exito')
    return mensajes

class ahorros():
    Oficina = None
    num_cta = None
    fecha_liq = None
    saldo_fecha = 0.0

    def __init__(self, iOficina, iFecha):
        self.Oficina = iOficina
        self.fecha_liq = iFecha

    def saldo_cta(self, inum_cta, ifecha=None):
        if ifecha == None:
            ifecha = self.fecha_liq
        self.num_cta = inum_cta
        resultado = DETALLE_PROD.objects.filter(
            producto = 'AH',
            subcuenta = self.num_cta,
            hecho_econo__fecha__lte = ifecha  # Asegura que la fecha sea <= '2025-05-06'
        ).aggregate(Sum('valor'))
        suma_valor = resultado['valor__sum'] if resultado['valor__sum'] is not None else 0
        self.saldo_fecha = suma_valor
        return


    def interes_mensual(self):
        if not es_ultimo_dia_del_mes(self.fecha_liq):
            print(
                'No se Puede liquidar el Interes Mensual si la fecha no es el ultimo dia del mes ')
            return
        Oficina = OFICINAS.objects.filter(codigo='A0001').first()
        Doc = DOCTO_CONTA.objects.filter(
            oficina=self.Oficina, per_con=self.fecha_liq.year, codigo=131).first()
        HecEco = HECHO_ECONO.objects.filter(
            docto_conta=Doc, numero=self.fecha_liq.timetuple().tm_yday).first()
        if HecEco == None:
            print('No se ha Realizado la Luiquidacion der Innteres diario a la fecha')
            return
        xUltDiaFec = ultimo_dia_mes_anterior(self.fecha_liq)
        print('Inicio Saldos Ahorro Mensual ', datetime.now())
        # Ctas = CTAS_AHORRO.objects.filter(oficina = self.Oficina,est_cta = 'A').exclude(Q(num_cta__startswith='04'))
        Ctas = CTAS_AHORRO.objects.filter(oficina=self.Oficina, est_cta='A').filter(Q(num_cta__startswith='01') | Q(
            num_cta__startswith='02') | Q(num_cta__startswith='06') | Q(num_cta__startswith='07'))
        saldo = 0
        conta = 0
        for Cta in Ctas:
            self.saldo_cta(Cta.num_cta, xUltDiaFec)
            xSalIni = self.saldo_fecha
            MovPers = DETALLE_ECONO.objects.filter(detalle_prod__producto='AH', detalle_prod__subcuenta=Cta.num_cta, hecho_econo__fecha__gt=xUltDiaFec,
                                                         hecho_econo__fecha__lte=self.fecha_liq, hecho_econo__docto_conta__oficina=Oficina).exclude(item_concepto='IntCor').order_by('hecho_econo__fecha')
            xFecAnt = xUltDiaFec
            xNueSal = xSalIni
            xSalPro = 0
            for MovPer in MovPers:
                xSalPro = xSalPro + xNueSal * \
                    (MovPer.hecho_econo.fecha - xFecAnt).days
                xFecAnt = MovPer.hecho_econo.fecha
                xNueSal = xNueSal + MovPer.debito - MovPer.credito
            LinAho = LINEAS_AHORRO.objects.filter(
                cliente=self.Oficina.cliente, cod_lin_aho=Cta.num_cta[0:2]).first()
            TasLin = TAS_LIN_AHO.objects.filter(
                lin_aho=LinAho, fecha_inicial__lte=self.fecha_liq, fecha_final__gte=self.fecha_liq).first()
            TasRF = RET_FUE_AHO.objects.filter(
                lin_aho=LinAho, fecha_inicial__lte=self.fecha_liq, fecha_final__gte=self.fecha_liq).first()
            xTasAnuEfe = TasLin.tiae / 100
            xTasIntMes = ((1+xTasAnuEfe/12)**(1/12)-1)*12
            xDiaMes = self.fecha_liq.day
            xSalPro = xSalPro + xNueSal*((self.fecha_liq - xFecAnt).days+1)
            xSalPro = round(xSalPro/xDiaMes, 0)
            xIntMes = round(xSalPro*xTasIntMes, 0)
            if xIntMes < 0:
                DetPro = DETALLE_PROD.objects.filter(
                    hecho_econo=HecEco, producto='AH', concepto='AHO', subcuenta=Cta.num_cta).first()
                if DetPro == None:
                    DetPro = DETALLE_PROD.objects.create(
                        hecho_econo=HecEco, producto='AH', concepto='AHO', subcuenta=Cta.num_cta)
                DetPro.save()
                ImpCon = IMP_CON_LIN_AHO.objects.filter(
                    linea_ahorro=LinAho, cod_imp=Cta.cod_imp).first()
                PlaCtaCta = PLAN_CTAS.objects.filter(
                    cliente=self.Oficina.cliente, per_con=self.fecha_liq.year, cod_cta=ImpCon.ctaafeact).first()
                DetEcoMov = DETALLE_ECONO.objects.filter(
                    hecho_econo=HecEco, cuenta=PlaCtaCta, tercero=Cta.asociado.tercero).first()
                if DetEcoMov == None:
                    DetEcoMov = DETALLE_ECONO.objects.create(
                        hecho_econo=HecEco, cuenta=PlaCtaCta, tercero=Cta.asociado.tercero)
                DetEcoMov.detalle_prod = DetPro
                DetEcoMov.item_concepto = 'IntCor'
                DetEcoMov.detalle = 'IntCor del Mes.  Cta '+Cta.num_cta
                DetEcoMov.debito = 0
                DetEcoMov.credito = -xIntMes
                DetEcoMov.valor_1 = 0
                DetEcoMov.valor_2 = 0
                DetEcoMov.save()
                if -xIntMes > TasRF.bas_liq_int * xDiaMes:
                    xDesRet = round(-xIntMes * TasRF.tas_liq_rf/100, 0)
                    PlaCtaCta = PLAN_CTAS.objects.filter(
                        cliente=self.Oficina.cliente, per_con=self.fecha_liq.year, cod_cta=ImpCon.ctaretfue).first()
                    DetEcoMovRet = DETALLE_ECONO.objects.filter(
                        hecho_econo=HecEco, cuenta=PlaCtaCta, tercero=Cta.asociado.tercero).first()
                    if DetEcoMovRet == None:
                        DetEcoMovRet = DETALLE_ECONO.objects.create(
                            hecho_econo=HecEco, cuenta=PlaCtaCta, tercero=Cta.asociado.tercero)
                    DetEcoMov.detalle_prod = DetPro
                    DetEcoMov.item_concepto = 'IntCor'
                    DetEcoMov.detalle = 'Ret Fte del Mes.  Cta '+Cta.num_cta
                    DetEcoMov.debito = xDesRet
                    DetEcoMov.credito = 0
                    DetEcoMov.valor_1 = 0
                    DetEcoMov.valor_2 = 0
                    DetEcoMov.save()

        IntDias = INT_DIA_AHO.objects.filter(aplicado='N', fecha__month=self.fecha_liq.month, oficina=Oficina).values(
            'num_cta').annotate(total_int=Sum('int_dia'), total_ret_fue=Sum('ret_fue'))
        for IntDia in IntDias:
            if IntDia['total_int'] >= 0:
                continue
            CtaAho = CTAS_AHORRO.objects.filter(
                oficina=self.Oficina, num_cta=IntDia['num_cta']).first()
            LinAho = LINEAS_AHORRO.objects.filter(
                cliente=self.Oficina.cliente, cod_lin_aho=CtaAho.num_cta[0:2]).first()
            DetPro = DETALLE_PROD.objects.filter(
                hecho_econo=HecEco, producto='AH', concepto='AHO', subcuenta=IntDia['num_cta']).first()
            if DetPro == None:
                DetPro = DETALLE_PROD.objects.create(
                    hecho_econo=HecEco, producto='AH', concepto='AHO', subcuenta=IntDia['num_cta'])
            DetPro.save()
            ImpCon = IMP_CON_LIN_AHO.objects.filter(
                linea_ahorro=LinAho, cod_imp=CtaAho.cod_imp).first()
            PlaCtaCta = PLAN_CTAS.objects.filter(
                cliente=self.Oficina.cliente, per_con=self.fecha_liq.year, cod_cta=ImpCon.ctaafeact).first()
            DetEcoMov = DETALLE_ECONO.objects.filter(
                hecho_econo=HecEco, cuenta=PlaCtaCta, tercero=Cta.asociado.tercero).first()
            if DetEcoMov == None:
                DetEcoMov = DETALLE_ECONO.objects.create(
                    hecho_econo=HecEco, cuenta=PlaCtaCta, tercero=CtaAho.asociado.tercero)
            DetEcoMov.detalle_prod = DetPro
            DetEcoMov.item_concepto = 'IntCor'
            DetEcoMov.detalle = 'IntCor Diario del Mes  Cta '+CtaAho.num_cta
            DetEcoMov.debito = 0
            DetEcoMov.credito = -IntDia['total_int']
            DetEcoMov.valor_1 = 0
            DetEcoMov.valor_2 = 0
            DetEcoMov.save()
            if IntDia['total_ret_fue'] > 0:
                PlaCtaCta = PLAN_CTAS.objects.filter(
                    cliente=self.Oficina.cliente, per_con=self.fecha_liq.year, cod_cta=ImpCon.ctaretfue).first()
                DetEcoMovRet = DETALLE_ECONO.objects.filter(
                    hecho_econo=HecEco, cuenta=PlaCtaCta, tercero=Cta.asociado.tercero).first()
                if DetEcoMovRet == None:
                    DetEcoMovRet = DETALLE_ECONO.objects.create(
                        hecho_econo=HecEco, cuenta=PlaCtaCta, tercero=Cta.asociado.tercero)
                DetEcoMov.detalle_prod = DetPro
                DetEcoMov.item_concepto = 'IntCor'
                DetEcoMov.detalle = 'Ret Fte diario del Mes.  Cta '+Cta.num_cta
                DetEcoMov.debito = IntDia['total_ret_fue']
                DetEcoMov.credito = 0
                DetEcoMov.valor_1 = 0
                DetEcoMov.valor_2 = 0
                DetEcoMov.save()

        print('Saldo MensuaL ', saldo, '  Cuentas', conta)
        print('Final Saldos Ahorro  Mensual ', datetime.now())
        return


def tarea_liq_int_diario():
    max_fecha = INT_DIA_AHO.objects.filter(aplicado='N').aggregate(Max('fecha'))['fecha__max']
    if max_fecha is None:
        max_fecha = date(2025,7,17)
    fecha_limite = date.today()
    fecha_liq = max_fecha + timedelta(days=1)
    while fecha_liq <= fecha_limite:
        print('Fecha a liquidar:', fecha_liq)
        with open("C:/aaa/liquidacion_diaria_hoy.txt", "a") as f:
            f.write(f"Fecha a liquidar: {fecha_liq}\n")
        mensajes = liquidar_int_diario_y_cdat(fecha_liq)
        if mensajes:
            asunto = mensajes[-1]
            cuerpo = "\n".join(mensajes)
            email = EmailMessage(
                subject=asunto,
                body=cuerpo,
                from_email=settings.EMAIL_HOST_USER,
                to=['chmanosalva@gmail.com'],
            )
            email.send()
        else:
            print("No hay mensajes para enviar.")
        fecha_liq += timedelta(days=1)
    return