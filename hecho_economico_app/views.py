import time, re, json, locale
from io import BytesIO
from math import ceil
from textwrap import wrap
from django_xhtml2pdf.views import PdfMixin
from django_xhtml2pdf.utils import generate_pdf
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.utils.dateformat import format

from justo_app.opciones import OPC_CANALES
from num2words import num2words
from clientes_app.models import CLIENTES
from oficinas_app.models import OFICINAS
from .models import HECHO_ECONO
from documentos_app.models import DOCTO_CONTA
from detalle_producto_app.models import DETALLE_PROD
from localidades_app.models import LOCALIDADES
from conceptos_app.models import CONCEPTOS
from creditos_app.models import CREDITOS
from cambios_creditos_app.models import CAMBIOS_CRE
from causacion_creditos_app.models import CREDITOS_CAUSA
from asociados_app.models import ASOCIADOS
from detalle_economico_app.models import DETALLE_ECONO
from cuentas_app.models import PLAN_CTAS
from ctas_ahorros_app.models import CTAS_AHORRO
from contabilizacion_lineas_ahorros_app.models import IMP_CON_LIN_AHO
from contabilizacion_capital_creditos_app.models import IMP_CON_CRE
from cxc_app.models import CTAS_X_COBRAR
from auditoria_app.models import AuditLog
from terceros_app.models import TERCEROS
from justo_app.justo_creditos import Liquida_cre
from .forms import HechoEconoForm
from django.db.models import Max

def gomonth(fecha, meses):
    return fecha + relativedelta(months=meses)

def asignar_fecha(fecha_str,formato='%d/%m/%Y'):
    try:
        fecha = datetime.strptime(fecha_str, formato)
        fecha_pura = fecha.date()  # Esto devuelve un objeto de tipo date
        return fecha_pura
    except ValueError:
        return None
DATE_PATTERN = re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$')

@require_GET
def get_consecutivo_plus_one(request):
    docto_conta_id = request.GET.get('docto_conta_id')
    try:
        if docto_conta_id:
            docto_conta = DOCTO_CONTA.objects.get(pk=docto_conta_id)
            print('entra 2',docto_conta_id,'   automatico ',docto_conta.num_automatico)
            if docto_conta.num_automatico == 'S':
                max_numero = HECHO_ECONO.objects.filter(docto_conta=docto_conta).aggregate(Max('numero'))['numero__max'] or 0
                consecutivo_plus_one = max_numero + 1
            else:
                consecutivo_plus_one = 0
            print('docto_conta ',docto_conta_id,'   consecutivo  ',consecutivo_plus_one)
            return JsonResponse({'consecutivo_plus_one': consecutivo_plus_one})
        else:
            return JsonResponse({'error': 'No se proporcionó docto_conta_id.'}, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'DoctoConta no encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#  Funciones Independientes 
def validate_details(form,cliente_id,oficina_id,fecha,crud):   # Pre Validacion
    print('Entra a Validacion ',oficina_id)
    errors = {}
    detalles = form.data.get('detalles', [])
    for detalle in detalles:
        id_str = detalle.get('id')
        try:
            id = int(id_str)
        except (TypeError, ValueError):
            id = id_str  # O maneja el error de acuerdo a tu lógica
        if crud == 'U' and id > 0:  # no debe tocar ni validar lo ya validado
            continue
        concepto = detalle.get('concepto')
        subcuenta = detalle.get('subcuenta')
        valor = detalle.get('valor')
        print('concepto',concepto,'  subcuenta ---->',subcuenta,'  Valor -----> ',valor,'   cliente_id ',cliente_id)    
        concepto1 = CONCEPTOS.objects.filter(cliente_id=1,cod_con = concepto).first()
        if concepto1 == None:
            errors['concepto'] = 'El concepto --> '+concepto+' No Existe'
            return errors
        huella = 'Concepto --> '+concepto+'  Subcuenta --> '+subcuenta
        if concepto1.tip_sis == '1':
            val_tran = valor
#  ------------------------------      Ahorros    ---------------------------- 
        elif concepto1.tip_sis == '2':
            val_tran = valor
#  ------------------------------      creditos    ---------------------------- 
        elif concepto1.tip_sis == '3':
            credito1 = CREDITOS.objects.filter(oficina_id = oficina_id,cod_cre = subcuenta).first()
            if credito1.estado == 'C':
                print('credito cancelado')
                errors[huella] = 'La fecha debe estar en formato dd/mm/yyyy 1'
                return errors
            if concepto == 'DESEM':
                val_tran = valor    
                if credito1.fec_des != fecha:
                    errors[huella] = ' La fecha de desembolso debe ser igual a la fecha del comprobante '
                    return errors
                if credito1.cap_ini != valor:
                    errors[huella] = ' El valor del desembolso no es igual al capital inicial del credito '
                    return errors
                if (credito1.fec_pag_ini - credito1.fec_des).days > 59:
                    errors[huella] = ' La fecha del pago inicial debe ser maximo dos periodos superio a la fecha de desembolso'
                    return errors
                if (credito1.fec_pag_ini - credito1.fec_des).days < 1:
                    errors[huella] = ' La fecha del pago inicial debe ser Mayor a la fecha de desembolso'
                    return errors
            else:
                val_tran = -valor
                if val_tran < 1:
                    print('Transacion ')
                    errors[huella] =' El Valor de la Transaccion debe ser Credito'
                    return errors
                if credito1.fec_ult_pag > fecha:
                    errors[huella] = ' Existe un pago Posterior por lo cual no se puede anexar este movimiento'
                    return errors
                liq_credito = Liquida_cre(subcuenta,fecha)
                liq_credito.liq_al_dia(fecha)                   
                if concepto == 'CUOTA':
                    if liq_credito.max_pag_couta < val_tran:
                        print('credito debe ser aboca ',liq_credito.max_pag_couta)
                        # errors[huella] = ' Con este valor debe usar el concepto ABOCA'
                    #return errors
                elif concepto == 'ABOCA':
                    if liq_credito.min_pag_aboca >= val_tran:
                        errors[huella] = ' Con Este valor no Puede abonar a capital'
                        return errors
                elif concepto == 'ABOCU':
                    if liq_credito.min_pag_abocu >= val_tran:
                        errors[huella] = ' Con este valor puede usar CUOTA o ABOCA'
                        return errors
    
    return errors

def valida_eliminados(hecho_econo_id, form):
    print('Entra a Validacion Eliminados ',hecho_econo_id)
    errors = {}
    detalles = form.data.get('detalles', [])
    hec_eco = HECHO_ECONO.objects.filter(id = hecho_econo_id).first()
    det_pro_exis = DETALLE_PROD.objects.filter(hecho_econo = hec_eco)
    for det_pro in det_pro_exis:
        print('Entra al For ')
        registro = next(
            (d for d in detalles 
            if (isinstance(d.get('id'), int) and d.get('id') == det_pro.id) or
                (isinstance(d.get('id'), str) and d.get('id').isdigit() and int(d.get('id')) == det_pro.id)
            ), 
            None
        )
        print('continua 1 ')
        if registro is None:  #  significa que lo borro para proteger la integridad se valida si se podia borrar el detalle
            huella = 'Concepto --> '+det_pro.concepto+'  Subcuenta --> '+det_pro.subcuenta
            conc_busc = CONCEPTOS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente_id,cod_con = det_pro.concepto).first()
            if conc_busc.tip_sis == '1':    
                aporte = ''     
            elif conc_busc.tip_sis == '2':    
                ahorro_ = ''
            elif conc_busc.tip_sis == '3':
                credito = CREDITOS.objects.filter(oficina_id = hec_eco.docto_conta.oficina_id).first()
                if credito.fec_ult_pag == None:    #  siempre debe estar cargado este campo
                    credito.fec_ult_pag = credito.fec_des
                    credito.save()
                if credito.fec_ult_pag > hec_eco.fecha :
                    errors[huella] = ' No se puede Eliminar un Registro de Cartera si hay un pago de Fecha Posterior'
                    return errors
            elif conc_busc.tip_sis == '4':
                cxc = ''
    return errors

def eliminar_eliminados(hecho_econo_id, form):
    detalles = form.data.get('detalles', [])
    hec_eco = HECHO_ECONO.objects.filter(id = hecho_econo_id).first()
    det_pro_exis = DETALLE_PROD.objects.filter(hecho_econo = hec_eco)
    print('Entra a Eliminar Eliminados ',hecho_econo_id)
    for det_pro in det_pro_exis:
        print('dep_pro ',det_pro.concepto)
        registro = next(
            (d for d in detalles 
            if (isinstance(d.get('id'), int) and d.get('id') == det_pro.id) or
                (isinstance(d.get('id'), str) and d.get('id').isdigit() and int(d.get('id')) == det_pro.id)
            ), 
            None
        )
        if registro is None:  #  significa que lo borro para proteger la integridad se valida si se podia borrar el detalle
            if det_pro.concepto == 'ABOCA' or det_pro.concepto == 'ABOCU':
                CREDITOS_CAUSA.objects.filter(cod_cre = det_pro.subcuenta,comprobante_id = None).delete()
                CREDITOS_CAUSA.objects.filter(cod_cre=det_pro.subcuenta,comprobante_id=hec_eco.id).update(comprobante_id=None)
            DETALLE_ECONO.objects.filter(hecho_econo_id = hec_eco.id,detalle_prod_id = det_pro.id).delete()
            det_pro.delete()
            
def save_or_update_details(hecho_econo_id, form):
    print('Entra a Validacion ',hecho_econo_id)
    errors = {}
    detalles = form.data.get('detalles', [])
    hec_eco = HECHO_ECONO.objects.filter(id = hecho_econo_id).first()
    per_con = hec_eco.docto_conta.per_con
    for detalle in detalles:
        id = detalle.get('id')
        id = int(id)
        concepto = detalle.get('concepto')
        subcuenta = detalle.get('subcuenta')
        valor = detalle.get('valor')
        detalle_item = detalle.get('det_pro')
        concepto1 = CONCEPTOS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente_id , cod_con = concepto).first()
        huella = 'id ---> '+str(id)+'  concepto ---> '+concepto+'  subcuenta --->'+subcuenta 
        print(f"Valor de id: {id}, Tipo: {type(id)}")
        if id > 0:
            det_pro  = DETALLE_PROD.objects.filter(id = id).first()
            if det_pro != None:
                if det_pro.concepto != concepto or det_pro.subcuenta != subcuenta or det_pro.valor != valor :
                    errors[huella] = 'No se Puede Re grabar una transaccion con valores diferentes  '
                    return errors 
                continue
        else:
#  ------------------------------      Aportes    ---------------------------- 
            if concepto1.tip_sis == '1':
                det_enc = 'Prd --> AP  '+'Cpto--> '+concepto+'  SbCta --> '+subcuenta
                detalle_prod = DETALLE_PROD.objects.create(hecho_econo_id = hec_eco.id,centro_costo_id = 1,
                    producto = 'AP',concepto = concepto,subcuenta = subcuenta,valor = valor,oficina_id = hec_eco.docto_conta.oficina_id)
                detalle_prod.save()
                socio = ASOCIADOS.objects.filter(cod_aso = subcuenta,oficina_id = hec_eco.docto_conta.oficina_id).first()
                cuenta = PLAN_CTAS.objects.filter(cod_cta = concepto1.cta_con,per_con = per_con,cliente_id = hec_eco.docto_conta.oficina.cliente_id).first()
                detalle_econo = DETALLE_ECONO.objects.create(
                    detalle_prod_id = detalle_prod.id,
                    item_concepto = concepto1.cod_con,
                    detalle = det_enc+"|"+detalle_item,
                    cuenta_id = cuenta.id,
                    tercero_id = socio.tercero_id,
                    debito = valor if valor >= 0 else 0,
                    credito = -valor if valor < 0 else 0,
                    hecho_econo_id = hec_eco.id,
                    valor_1 = 0,
                    valor_2 = 0)
#  ------------------------------      Ahorros    ---------------------------- 
            elif concepto1.tip_sis == '2':
                det_enc = 'Prd --> AH  '+'Cpto--> '+concepto+'  SbCta --> '+subcuenta
                detalle_prod = DETALLE_PROD.objects.create(hecho_econo_id = hec_eco.id,centro_costo_id = 1,
                    producto = 'AH',concepto = concepto,subcuenta = subcuenta,valor = valor)
                detalle_prod.save()
                print('Ahorros 1')
                cta_aho = CTAS_AHORRO.objects.filter(oficina_id = hec_eco.docto_conta.oficina_id,num_cta = subcuenta).first()
                if cta_aho == None:
                    return JsonResponse({'success': False, 'error': 'Cta Contable No Existe'}, status=400) 
                print('Ahorros 2')
                socio = ASOCIADOS.objects.filter(oficina_id = hec_eco.docto_conta.oficina_id,id = cta_aho.asociado_id).first()
                if socio == None:
                    return JsonResponse({'success': False, 'error': 'Asociado No Existe'}, status=400) 
                print('Ahorros 3')
                ic_lin_aho = IMP_CON_LIN_AHO.objects.filter(cod_imp = cta_aho.cod_imp).first()
                if ic_lin_aho == None:
                    return JsonResponse({'success': False, 'error': 'Imp Contable No Existe'}, status=400) 
                print('Ahorros 4')
                cta_con_aho = PLAN_CTAS.objects.filter(cliente_id = 1,per_con = per_con,cod_cta = ic_lin_aho.ctaafeact).first()
                if cta_con_aho == None:
                    return JsonResponse({'success': False, 'error': 'Cta Contable ahorro no existe'}, status=400) 
                print('Ahorros 5')
                detalle_econo = detalle_econo = DETALLE_ECONO.objects.create(
                    detalle_prod_id = detalle_prod.id,
                    item_concepto = 'deposi' if valor < 0 else 'Retiro',
                    detalle = det_enc+"|"+detalle_item,
                    cuenta_id = cta_con_aho.id,
                    tercero_id = socio.tercero_id,
                    debito = valor if valor >= 0 else 0,
                    credito = -valor if valor < 0 else 0,
                    hecho_econo_id = hec_eco.id,
                    valor_1 = 0,
                    valor_2 = 0)
#  ------------------------------      Creditos    ---------------------------- 
            elif concepto1.tip_sis == '3':
                det_enc = 'Prd --> CR  '+'Cpto--> '+concepto+'  SbCta --> '+subcuenta
               
                credito = CREDITOS.objects.filter(oficina_id = hec_eco.docto_conta.oficina_id,cod_cre = subcuenta).first()    
                imp_con_cre = IMP_CON_CRE.objects.filter(id = credito.imputacion_id ).first()
                socio = ASOCIADOS.objects.filter(id = credito.socio_id).first()
                if concepto == 'CUOTA' or concepto == 'ABOCA' or concepto == 'ABOCU':
                    liq_credito = Liquida_cre(subcuenta,hec_eco.fecha)
                    if concepto == 'CUOTA':
                        liq_credito.distri_pago_cuota(-valor)
                    else:
                        print('liq_credito.distri_pago_abo ---> ',liq_credito.distri_pago_abo(-valor))
                    print('Hecho Econo Fecha ----> ',hec_eco.fecha)
                    print('kapiTAl ',liq_credito.capital_a_pag)
                    print('iNt cor ',liq_credito.int_cor_a_pag )
                    print('intmOr ',liq_credito.int_mor_a_pag)
                    detalle_prod = DETALLE_PROD.objects.create(hecho_econo_id = hec_eco.id,oficina_id = hec_eco.docto_conta.oficina_id,
                        centro_costo_id = 1,producto = 'CR',concepto = concepto,subcuenta = subcuenta,valor = valor)
                    detalle_prod.save()
                    if liq_credito.capital_a_pag != 0:
                        plan_ctas = PLAN_CTAS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente.id ,per_con = per_con,cod_cta = imp_con_cre.kpte_cap).first()  
                        detalle_econo = DETALLE_ECONO.objects.create(detalle_prod_id = detalle_prod.id,hecho_econo_id = hec_eco.id,
                            tercero_id = socio.tercero_id,item_concepto = 'Kapita',cuenta_id = plan_ctas.id,
                            detalle = det_enc+'  Kap '+"|"+detalle_item,
                            debito = -liq_credito.capital_a_pag if liq_credito.capital_a_pag < 0 else 0,
                            credito = liq_credito.capital_a_pag if liq_credito.capital_a_pag > 0 else 0,
                            valor_1 = -liq_credito.capital_a_pag if liq_credito.capital_a_pag < 0 else 0,
                            valor_2 = liq_credito.capital_a_pag if liq_credito.capital_a_pag > 0 else 0)
                        detalle_econo.save()
                    if liq_credito.int_cor_a_pag != 0:                  
                        plan_ctas = PLAN_CTAS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente_id,per_con = per_con,cod_cta = imp_con_cre.kpte_ic.strip()).first()            
                        detalle_econo = DETALLE_ECONO.objects.create(detalle_prod_id = detalle_prod.id,hecho_econo_id = hec_eco.id,
                            tercero_id = socio.tercero_id,item_concepto = 'IntCor',cuenta_id = plan_ctas.id,
                            detalle = det_enc+'  IC '+"|"+detalle_item,
                            debito = -liq_credito.int_cor_a_pag if liq_credito.int_cor_a_pag < 0 else 0,
                            credito = liq_credito.int_cor_a_pag if liq_credito.int_cor_a_pag > 0 else 0,
                            valor_1 = -liq_credito.int_cor_a_pag if liq_credito.int_cor_a_pag < 0 else 0,
                            valor_2 = liq_credito.int_cor_a_pag if liq_credito.int_cor_a_pag > 0 else 0)
                        detalle_econo.save()
                    if liq_credito.int_mor_a_pag != 0:
                        plan_ctas = PLAN_CTAS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente_id,per_con = per_con,cod_cta = '41504001').first()
                        detalle_econo = DETALLE_ECONO.objects.create(detalle_prod_id = detalle_prod.id,hecho_econo_id = hec_eco.id,
                            tercero_id = socio.tercero_id,item_concepto = 'IntMor',cuenta_id = plan_ctas.id,
                            detalle = det_enc+'  IM '+"|"+detalle_item,
                            debito = -liq_credito.int_mor_a_pag if liq_credito.int_mor_a_pag < 0 else 0,
                            credito = liq_credito.int_mor_a_pag if liq_credito.int_mor_a_pag > 0 else 0,
                            valor_1 = -liq_credito.int_mor_a_pag if liq_credito.int_mor_a_pag < 0 else 0,
                            valor_2 = liq_credito.int_mor_a_pag if liq_credito.int_mor_a_pag > 0 else 0)
                        detalle_econo.save()
                    if (liq_credito.aju_ic_a_pag != 0 or liq_credito.int_mor_cau):
                        cambios_cre = CAMBIOS_CRE.objects.create(det_pro_id = detalle_prod.id,tip_cam = '2',
                            fecha = hec_eco.fecha,capital = 0,
                            int_cor = liq_credito.aju_ic_a_pag,
                            int_mor = liq_credito.int_mor_cau,
                            pol_seg = 0,acreedor = 0,des_pp = 0)
                        cambios_cre.save()
                        credito.fec_ult_pag = hec_eco.fecha
                        credito.estado = credito.estado if liq_credito.sal_cap_tot > liq_credito.capital_a_pag else 'C'
                        credito.save()
                if concepto == 'DESEM':
                    detalle_prod = DETALLE_PROD.objects.create(hecho_econo_id = hec_eco.id,oficina_id = hec_eco.docto_conta.oficina_id,
                        centro_costo_id = 1,producto = 'CR',concepto = concepto,subcuenta = subcuenta,valor = valor)
                    detalle_prod.save()
                    
                    causacion_credito(hec_eco.id,hec_eco.docto_conta.oficina_id, subcuenta)
                    plan_ctas = PLAN_CTAS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente_id,per_con = per_con,cod_cta = imp_con_cre.kpte_cap.strip()).first()          
                    detalle_econo = DETALLE_ECONO.objects.create(detalle_prod = detalle_prod,hecho_econo_id = hec_eco.id,
                        tercero_id = socio.tercero_id,item_concepto = 'Desem',cuenta_id = plan_ctas.id,
                        detalle = det_enc+'  DES '+"|"+detalle_item,
                        debito = valor,
                        credito = 0,
                        valor_1 = valor,
                        valor_2 = 0)
                    detalle_econo.save()
                if concepto != 'CUOTA' and concepto != 'DESEM' :     #  debe quedar memoria de la causacion anterior
                    print('memoria de la causacion anterior')
                    liq_credito = Liquida_cre(subcuenta,hec_eco.fecha)
                    xIntCauFra = liq_credito.int_cau_fra
                    liq_cre = Liquida_cre(subcuenta,hec_eco.fecha)
                    sal_x_dis = liq_cre.sal_cap_tot
                    cap_x_apl = liq_cre.cap_ini
                    cap_pagado = liq_cre.cap_ini - liq_cre.sal_cap_tot
                    xIntMes = liq_cre.int_cor_a_pag
                    print('Capital pagado ',cap_pagado)
                    lista_causa = CREDITOS_CAUSA.objects.filter(oficina_id = 1,cod_cre = subcuenta,comprobante_id__isnull=True).order_by('cuota')
                    if lista_causa == None:
                        print('Error lista causa ')
                    else:
                        print('lista causa oK ')
                    xFecAnt = hec_eco.fecha 
                    xCuota = 0
                    for obj in lista_causa:
                        obj.comprobante_id = hec_eco.id
                        obj.save()
                        if obj.fecha <= hec_eco.fecha:
                            xCuota = obj.cuota
                            cap_x_apl = cap_x_apl - obj.capital
                            nue_caus = CREDITOS_CAUSA.objects.create(oficina=obj.oficina,
                                cod_cre = obj.cod_cre,
                                cuota = obj.cuota, 
                                fecha = obj.fecha,
                                capital = obj.capital,
                                int_cor = obj.int_cor,
                                comprobante = None)
                            nue_caus.save()
                        else:
                            if cap_x_apl > 0 :
                                if obj.cuota == xCuota + 1 and concepto == 'ABOCU': 
                                    xCapPer = liq_credito.val_cuo - xIntMes if liq_credito.val_cuo - xIntMes <= cap_x_apl  else cap_x_apl
                                    nue_caus = CREDITOS_CAUSA.objects.create(oficina=obj.oficina,
                                        cod_cre = obj.cod_cre,
                                        cuota = obj.cuota, 
                                        fecha = obj.fecha,
                                        capital = 0,
                                        int_cor = xIntCauFra,
                                        comprobante = None)
                                    xIntCauFra = 0
                                    nue_caus.save()
                                else:
                                    if cap_x_apl <= 0:
                                        nue_caus = CREDITOS_CAUSA.objects.create(oficina=obj.oficina,
                                            cod_cre = obj.cod_cre,
                                            cuota = obj.cuota, 
                                            fecha = obj.fecha,
                                            capital = cap_x_apl,
                                            int_cor = xIntCauFra,
                                            comprobante = None)
                                        nue_caus.save()
                                        xIntCauFra = 0
                                        cap_x_apl = 0
                                    else:
                                        xCapBas = cap_x_apl - liq_cre.sal_cap_tot if cap_x_apl - liq_cre.sal_cap_tot > 0 else 0
                                        print('xCapBas -----> ',xCapBas,'  liq_cre.sal_cap_tot',liq_cre.sal_cap_tot)
                                        print('cuota -------> ',obj.cuota,' FECHA ',obj.fecha,'  cap_x_apl  ',cap_x_apl,'   cap_pagado ',liq_cre.sal_cap_tot)
                                        xIntMes = round(sal_x_dis * liq_credito.tas_ic_dia,0) * (obj.fecha - xFecAnt).days 
                                        print('xIntMes -----> ',xIntMes)
                                        xCapPer = xCapBas + liq_credito.val_cuo - xIntMes if liq_credito.val_cuo - xIntMes < cap_x_apl else cap_x_apl
                                        print('xCapPer-----> ',xCapPer)
                                        xCapPer = xCapPer if xCapPer < xCapBas else xCapBas 
                                        xCapPer = cap_x_apl if xCapPer == 0 else xCapPer
                                        nue_caus = CREDITOS_CAUSA.objects.create(oficina=obj.oficina,
                                            cod_cre = obj.cod_cre,
                                            cuota = obj.cuota, 
                                            fecha = obj.fecha,
                                            capital = xCapPer,
                                            int_cor = xIntMes + xIntCauFra,
                                            comprobante = None)
                                        nue_caus.save()
                                        xIntCauFra = 0
                                        cap_x_apl = cap_x_apl - xCapPer
                                        sal_x_dis = sal_x_dis - xCapPer + xCapBas
                                        sal_x_dis = sal_x_dis if sal_x_dis > 0 else 0
                                        xFecAnt = obj.fecha
                            else:
                                nue_caus = CREDITOS_CAUSA.objects.create(oficina=obj.oficina,
                                    cod_cre = obj.cod_cre,
                                    cuota = obj.cuota, 
                                    fecha = obj.fecha,
                                    capital = 0,
                                    int_cor = xIntCauFra,
                                    comprobante = None)
                                xIntCauFra = 0
                                nue_caus.save()

#  ---------------------------- Conceptos Contables    ---------------------------- 
            elif concepto1.tip_sis == '4': 
                det_enc = 'Prd --> CJ  '+'Cpto--> '+concepto+'  SbCta --> '+subcuenta
                detalle_prod = DETALLE_PROD.objects.create(hecho_econo_id = hec_eco.id,
                    oficina_id = hec_eco.docto_conta.oficina_id,centro_costo_id = 1,
                    producto = 'BN',concepto = concepto,subcuenta = subcuenta,valor = valor)
                detalle_prod.save()
                print('Entro a Plan')
                cta_con = PLAN_CTAS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente_id,per_con = per_con,
                    cod_cta = subcuenta).first()
                print('Entro a Subcuenta')
                tercero = TERCEROS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente.id,doc_ide=hec_eco.docto_conta.oficina.cliente.doc_ide).first()
                detalle_econo = DETALLE_ECONO.objects.create(
                    detalle_prod_id = detalle_prod.id,
                    item_concepto = concepto1.cod_con,
                    detalle = det_enc+"|"+detalle_item,
                    cuenta_id = cta_con.id,
                    tercero_id = tercero.id,
                    debito = valor if valor >= 0 else 0,
                    credito = -valor if valor < 0 else 0,
                    hecho_econo_id = hec_eco.id,
                    valor_1 = 0,
                    valor_2 = 0)
                detalle_econo.save()

            elif concepto1.tip_sis == '5': 
                det_enc = 'Prd --> CJ  '+'Cpto--> '+concepto+'  SbCta --> '+subcuenta
                detalle_prod = DETALLE_PROD.objects.create(hecho_econo_id = hec_eco.id,
                    oficina_id = hec_eco.docto_conta.oficina_id,centro_costo_id = 1,
                    producto = 'EF',concepto = concepto,subcuenta = subcuenta,valor = valor)
                detalle_prod.save()
                cta_con = PLAN_CTAS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente_id,per_con = per_con,
                    cod_cta = concepto1.cta_con).first()
                tercero = TERCEROS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente.id,doc_ide=hec_eco.docto_conta.oficina.cliente.doc_ide).first()
                detalle_econo = DETALLE_ECONO.objects.create(
                    detalle_prod_id = detalle_prod.id,
                    item_concepto = concepto1.cod_con,
                    detalle = det_enc+"|"+detalle_item,
                    cuenta_id = cta_con.id,
                    tercero_id = tercero.id,
                    debito = valor if valor >= 0 else 0,
                    credito = -valor if valor < 0 else 0,
                    hecho_econo_id = hec_eco.id,
                    valor_1 = 0,
                    valor_2 = 0)
                detalle_econo.save()
            elif concepto1.tip_sis == '6': 
                det_enc = 'Prd --> CJ  '+'Cpto--> '+concepto+'  SbCta --> '+subcuenta
                print('Detallle ',det_enc)
                detalle_prod = DETALLE_PROD.objects.create(hecho_econo_id = hec_eco.id,
                    oficina_id = hec_eco.docto_conta.oficina_id,centro_costo_id = 1,
                    producto = 'CX',concepto = concepto,subcuenta = subcuenta,valor = valor)
                detalle_prod.save()
                print('Entro a Plan')
                cta_con = PLAN_CTAS.objects.filter(cliente_id = hec_eco.docto_conta.oficina.cliente_id,per_con = per_con,
                    cod_cta = concepto1.cta_con).first()
                cxc =  CTAS_X_COBRAR.objects.filter(oficina_id = hec_eco.docto_conta.oficina_id,cod_cxc = subcuenta).first()
                tercero = TERCEROS.objects.filter(id = cxc.tercero_id,).first()
                detalle_econo = DETALLE_ECONO.objects.create(
                    detalle_prod_id = detalle_prod.id,
                    detalle = det_enc+"|"+detalle_item,
                    item_concepto = concepto1.cod_con,
                    cuenta_id = cta_con.id,
                    tercero_id = tercero.id,
                    debito = valor if valor >= 0 else 0,
                    credito = -valor if valor < 0 else 0,
                    hecho_econo_id = hec_eco.id,
                    valor_1 = 0,
                    valor_2 = 0)
                detalle_econo.save()
     
class HechoEconoBaseView(View):

    def validate_models(self, form):
        errors = {}
        fecha = form.cleaned_data.get('fecha')
        if not isinstance(fecha, str):
            return errors
        if not self.is_valid_date_format(fecha):
            errors['fecha'] = 'La fecha debe estar en formato dd/mm/yyyy'
        if not DATE_PATTERN.match(fecha):
            errors['fecha1'] = 'La fecha debe estar en formato dd/mm/yyyy 1'
        docto_conta = form.cleaned_data.get('docto_conta')
        if not docto_conta:
            errors['docto_conta'] = 'Debe seleccionar un documento de contabilidad.'
        else:
            # Verifica que el valor seleccionado sea un objeto válido en la base de datos
            try:
                get_object_or_404(DOCTO_CONTA, pk=docto_conta.id)
            except ValidationError:
                errors['docto_conta'] = 'El documento de contabilidad seleccionado no es válido.'        
        return errors

    def is_valid_date_format(date_value):
        # Verificar si date_value es una cadena
        if isinstance(date_value, str):
            try:
                datetime.strptime(date_value, '%d/%m/%Y')
                return True
            except ValueError:
                return False
        # Verificar si date_value es un objeto datetime
        elif isinstance(date_value, (datetime, date)):
            return True
        else:
            return False

    def save_models(self, form):
        try:
            with transaction.atomic():
                # Guarda el modelo principal HechoEcono
                hecho_econo = form.save(commit=False)
                hecho_econo.save()
                print('entra a save ',hecho_econo)
                self.save_or_update_details(hecho_econo.id, form)
                self.save_or_update_accounting_details(hecho_econo, form)
        except Exception as e:
            # Maneja cualquier error que pueda ocurrir durante el guardado
            raise e

    def handle_errors(self, errors):
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        return None

class HechoEconoCreateView(HechoEconoBaseView, CreateView):
    model = HECHO_ECONO
    form_class = HechoEconoForm
    template_name = 'hecho_econo_form.html'
    success_url = reverse_lazy('hecho_econo_list')

    MAX_RETRIES = 3

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cliente_id'] = self.request.session.get('cliente_id')
        kwargs['oficina_id'] = self.request.session.get('oficina_id')
        kwargs['per_con'] = self.request.session.get('per_con')
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        # Verificar si las variables de sesión están inicializadas
        cliente_id = request.session.get('cliente_id')
        oficina_id = request.session.get('oficina_id')
        per_con = request.session.get('per_con')
        
        if cliente_id is None or oficina_id is None or per_con is None:
            # Agregar mensaje de error para el usuario
            messages.error(request, "Las variables de sesión no están inicializadas. Por favor, inicie sesión de nuevo.")
            # Redirigir a la vista de inicio de sesión
            return redirect('Iniciar_Sesion')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operation'] = 'create'  # Definir la operación como 'create'
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        print('GET Response Context:', response.context_data)
        return response

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        cliente_id = self.request.session.get('cliente_id')
        oficina_id = self.request.session.get('oficina_id')
        per_con = self.request.session.get('per_con')
        print('Inicia al Post   ', per_con)
        data = json.loads(request.body)
        form = HechoEconoForm(data)
        print('Datos recibidos:', data) 
        if form.is_valid():
            errors = self.validate_models(form)
            if errors:       
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': errors}, status=400)
            docto_conta = form.cleaned_data.get('docto_conta')
            numero = form.cleaned_data.get('numero')
            canal = form.cleaned_data.get('canal')
            fecha = form.cleaned_data.get('fecha')
            valor_comp = form.cleaned_data.get('valor')
            descripcion = form.cleaned_data.get('descripcion')
            anulado = form.cleaned_data.get('anulado')
            protegido = form.cleaned_data.get('protegido')
            ciudad_num = form.cleaned_data.get('ciudad').id
            banco = form.cleaned_data.get('banco')  # Obtiene el valor del campo banco
            banco_num = banco.id if banco else None 
            cheque = form.cleaned_data.get('cheque')
            beneficiario = form.cleaned_data.get('beneficiario')
            hay_error = validate_details(form,cliente_id,oficina_id,fecha,'C')
            if hay_error:
                print('retorno  por que hay error antes  ----> ',hay_error)
                hay_error = {key: [value] if isinstance(value, str) else value for key, value in hay_error.items()}
                print('retorno  por que hay error despues ---> ',hay_error)
                return JsonResponse({'success': False, 'errors': hay_error})        
            retries = 0
            while retries < self.MAX_RETRIES:
                try:
                    with transaction.atomic():
                        docto_conta_actualizado = DOCTO_CONTA.objects.select_for_update().get(id=docto_conta.id)
                        print('Empieza atomic ', docto_conta_actualizado.num_automatico)
                        if docto_conta_actualizado.num_automatico == 'N':
                            if HECHO_ECONO.objects.filter(docto_conta=docto_conta_actualizado, numero=numero).exists():
                                return JsonResponse({'success': False, 'error': 'Ya existe un Comprobante con ese Número'}, status=400)
                            else:
                                hecho_econo = HECHO_ECONO.objects.create(
                                    docto_conta=docto_conta_actualizado, numero=numero,
                                    canal=canal, 
                                    fecha = fecha,
                                    valor = valor_comp,
                                    descripcion=descripcion, anulado='S' if anulado else 'N',
                                    protegido='S' if protegido else 'N', ciudad_id=ciudad_num,
                                    banco_id=banco_num, cheque=cheque, beneficiario=beneficiario,
                                    user = self.request.user,
                                    usuario = self.request.user.username
                                )
                                hecho_econo.save()
                        #        break
                        else:
                            print('Num automatico Si ', docto_conta_actualizado.consecutivo + 1)
                            print('Anulado  ----------->',anulado)
                            try:
                                hecho_econo = HECHO_ECONO.objects.create(
                                docto_conta = docto_conta_actualizado, 
                                numero = numero,
                                canal = canal, 
                                fecha = fecha,
                                descripcion = descripcion, 
                                anulado = anulado,
                                protegido = protegido,
                                ciudad_id = ciudad_num,
                                banco_id = banco_num, 
                                cheque = cheque,
                                beneficiario = beneficiario,
                                valor = valor_comp,
                                user = self.request.user,
                                usuario = self.request.user.username
                                )
                                hecho_econo.save()
                                print('Se pudo grabar',hecho_econo)
                            except Exception as e:
                                print(f"Error al crear HECHO_ECONO: {e}")
                                return JsonResponse({'success': False, 'error': 'Fallos en el Registro de la Transacción'}, status=400)
                            docto_conta_actualizado.consecutivo = hecho_econo.numero
                            docto_conta_actualizado.save()
                        print('llamado 2 ',hecho_econo,'   id',hecho_econo.id)
                        save_or_update_details(hecho_econo.id, form)
                        break
                except IntegrityError as e:
                    retries += 1
                    if retries >= self.MAX_RETRIES:
                        return JsonResponse({'success': False, 'error': 'Fallos en el Registro de la Transacción'}, status=400)
                    else:
                        time.sleep(1)  # Esperar un segundo antes de reintentar
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Se grabó correctamente.','Numero' : hecho_econo.numero,'pk' : hecho_econo.id})
        
        else:
            if is_ajax:
                print('Retorna Los errores 1')
                return JsonResponse({'success': False, 'errors': form.errors})  

    def validate_models(self, form):
        # Implementa la lógica de validación
        return []

    def handle_errors(self, errors):
        # Implementa el manejo de errores
        return JsonResponse({'success': False, 'errors': errors})
       
    def save_or_update_accounting_details(self, hecho_econo, form):
        # Implementa el guardado o actualización de detalles contables
        pass

class HechoEconoUpdateView(View):
    MAX_RETRIES = 3

    def get(self, request, *args, **kwargs):
        # Lógica para manejar GET si es necesario
        pass

class HechoEconoUpdateView(HechoEconoBaseView,UpdateView):
    model = HECHO_ECONO  # Asegúrate de especificar el modelo correcto
    form_class = HechoEconoForm
    template_name = 'hecho_econo_form.html'
    MAX_RETRIES = 3

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cliente_id'] = self.request.session.get('cliente_id')
        kwargs['oficina_id'] = self.request.session.get('oficina_id')
        kwargs['per_con'] = self.request.session.get('per_con')
        return kwargs

    def get_context_data(self, **kwargs):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        hecho_econo = self.get_object()  # Obtén el objeto principal
        detalles = hecho_econo.detalles.all()
        context['operation'] = 'update'  # Definir la operación como 'update'
        context['detalle_prod_list'] = detalles  # Añadir los detalles al contexto
        context['object'] = self.object 
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        hecho_econo = get_object_or_404(HECHO_ECONO, pk=kwargs.get('pk'))
        detalles = hecho_econo.detalles.all() 
        for detalle in detalles:
            det_eco = DETALLE_ECONO.objects.filter(detalle_prod_id = detalle.id).first()
            if det_eco == None:
                detalle.det_concepto = ''
            else:
                texto_completo = det_eco.detalle
                indice = det_eco.detalle.find("|")
                if indice != -1:
                    detalle.det_concepto = texto_completo[indice+1:]  # Extraemos el texto desde el "|"
                else:
                    detalle.det_concepto = ''
        form = HechoEconoForm(instance=hecho_econo)
        context = {
            'form': form,
            'operation': 'update',
            'detalle_prod_list': detalles,
            'object' : self.object, 
        }
        print('Detalles ---------------> ',detalles)
        return render(request, 'hecho_econo_form.html', context)
    
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        cliente_id = self.request.session.get('cliente_id')
        oficina_id = self.request.session.get('oficina_id')
        per_con = self.request.session.get('per_con')
        data = json.loads(request.body)
        hecho_econo_id = self.kwargs.get('pk')  # Asumimos que el 'pk' llega en la URL o como argumento
        if hecho_econo_id:
            hecho_econo = get_object_or_404(HECHO_ECONO, pk=hecho_econo_id)
            form = HechoEconoForm(data, instance=hecho_econo)  # Pasar la instancia existente al formulario
        else:
            # Si no hay ID, significa que es un nuevo registro
            form = HechoEconoForm(data)
        print('Instancia en la vista:', form.instance.pk)

        if form.is_valid():
            print('Inicia is_valid ')
            errors = self.validate_models(form)
            if errors:       
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': errors}, status=400)
            print('Validacion Correcta 1')
            docto_conta = form.cleaned_data.get('docto_conta')
            numero = form.cleaned_data.get('numero')
            canal = form.cleaned_data.get('canal')
            fecha = form.cleaned_data.get('fecha')
            descripcion = form.cleaned_data.get('descripcion')
            anulado = form.cleaned_data.get('anulado')
            protegido = form.cleaned_data.get('protegido')
            print('protegido ---> ',protegido)
            ciudad_num = form.cleaned_data.get('ciudad').id
            banco = form.cleaned_data.get('banco')  # Obtiene el valor del campo banco
            banco_num = banco.id if banco else None 
            cheque = form.cleaned_data.get('cheque')
            beneficiario = form.cleaned_data.get('beneficiario')
            hay_error = validate_details(form,cliente_id,oficina_id,fecha,'U')
            print('va a mirar si hay error ----> ') 
            if hay_error: 
                print('Hay Error ----> ',hay_error)  
                hay_error = {key: [value] if isinstance(value, str) else value for key, value in hay_error.items()}
                return JsonResponse({'success': False, 'error': hay_error})
            print('Sale de validar detalles')
            if hecho_econo == None:
                return JsonResponse({'success': False, 'error': 'No existe un Comprobante con ese Número'}, status=400)
            else:
                print('Entra a gestion ')
                hay_borrados = valida_eliminados(hecho_econo_id, form)

                if len(hay_borrados) != 0:
                    print('retorno  ',hay_borrados)
                    return JsonResponse({'success': False, 'error': hay_borrados}, status=400)
                print('continua 1 ')
                if hecho_econo.docto_conta != docto_conta:
                    print('Docto Conta mal....')
                    return JsonResponse({'success': False, 'error': 'No se puede cambiar el documento de un comprobante ya grabado'})
                print('continua 2 ')
                if hecho_econo.fecha != fecha:
                    print('Fecha mal....')
                    return JsonResponse({'success': False, 'error': 'La fecha No se puede Cambiar deberia eliminar el comprobante'})
                print('continua 3 ')
                if protegido == 'S':
                    return JsonResponse({'success': False, 'error': 'El comprobante esta protegido no se puede grabar'})    
                print('Termina Validacion  ')
                try:
                    with transaction.atomic():
                        print('Entra a Atomic......')
                        hecho_econo.canal = canal
                        hecho_econo.descripcion = descripcion
                        hecho_econo.banco = banco
                        hecho_econo.cheque = cheque
                        hecho_econo.beneficiario = beneficiario
                        hecho_econo.ciudad_id = ciudad_num
                        hecho_econo.anulado=anulado
                        hecho_econo.protegido=protegido
                        hecho_econo.save()
                        eliminar_eliminados(hecho_econo.id, form)
                        print('Entra a save details ....')
                        save_or_update_details(hecho_econo.id, form)
                        if is_ajax:
                            print('Se pudo grabar y is_ajax')
                            return JsonResponse({'success': True, 'message': 'Se grabó correctamente.','numero' : hecho_econo.numero})
                        else:
                            print('Se pudo grabar y no is_ajax')
                            messages.success(request, 'Se grabó correctamente.')
                            return JsonResponse({'success': True})
                except IntegrityError as e:
                    print("Errores en el formulario 1:", form.errors)
                    if is_ajax:
                        print('Retorna Los errores 2')
                        return JsonResponse({'success': False, 'errors': form.errors})
        else:
            print("Errores en el formulario 2:", form.errors)
            if is_ajax:
                print('Retorna Los errores 3')
                return JsonResponse({'success': False, 'errors': form.errors})

def confirmar_eliminar_hecho_econo(request, pk):
    hecho_econo = get_object_or_404(HECHO_ECONO, pk=pk)    
    if request.method == "POST":
        deta_pros = DETALLE_PROD.objects.filter(hecho_econo = hecho_econo)
        errors = {}
        for deta_pro in deta_pros:
            if deta_pro.producto == 'CR':
                credito = CREDITOS.objects.filter(oficina = hecho_econo.docto_conta.oficina_id,cod_cre = deta_pro.subcuenta).first()
                if credito != None:
                    if credito.fec_ult_pag > hecho_econo.fecha:
                        errors[credito.cod_cre] = 'Existe un movimiento de pago Posterior en este Credito'
            elif deta_pro.producto == 'AP':
                hallado_apo = DETALLE_PROD.objects.filter(hecho_econo__docto_conta__oficina_id = hecho_econo.docto_conta.id,
                                                  producto='AP',subcuenta = deta_pro.subcuenta,
                                                  hecho_econo__fecha__gt=hecho_econo.fecha).first()
                if hallado_apo != None:
                    errors[deta_pro.subcuenta] = 'Existe un movimiento de pago Posterior en este aporte'
            elif deta_pro.producto == 'AH':
                hallado_aho = DETALLE_PROD.objects.filter(hecho_econo__docto_conta__oficina_id = hecho_econo.docto_conta.id,
                                                  producto='AH',subcuenta = deta_pro.subcuenta,
                                                  hecho_econo__fecha__gt=hecho_econo.fecha).first()
                if hallado_aho != None:
                    errors[deta_pro.subcuenta] = 'Existe un movimiento de pago Posterior en esta cuenta de Ahorros'
        if not errors:
            deta_pros = DETALLE_PROD.objects.filter(hecho_econo = hecho_econo)
            for deta_pro in deta_pros:
                if deta_pro.producto == 'CR' and (deta_pro.concepto == 'ABOCA' or deta_pro.concepto == 'ABOCU' or deta_pro.concepto == 'DESEM'):
                    print('entra a borrar causa cred ')
                    CREDITOS_CAUSA.objects.filter(cod_cre = deta_pro.subcuenta,comprobante_id = None).delete()
                    print('entra a actualizar causa cred ')
                    CREDITOS_CAUSA.objects.filter(cod_cre=deta_pro.subcuenta, comprobante_id=hecho_econo.id).update(comprobante_id=None)
                    CAMBIOS_CRE.objects.filter(det_pro_id = deta_pro.id ).delete()    
                    if deta_pro.concepto == 'DESEM':
                        credito = CREDITOS.objects.filter(oficina_id = 1, cod_cre = deta_pro.subcuenta).first()
                        if credito != None:
                            credito.com_des_id = None
                            credito.fec_ult_pag = credito.fec_des
                            credito.estado ='X'
                            credito.save()
            DETALLE_ECONO.objects.filter(hecho_econo = hecho_econo).delete()
            dets_pro_cre = DETALLE_PROD.objects.filter(hecho_econo = hecho_econo,producto = 'CR')
            for det_pro_cre in dets_pro_cre:
                CAMBIOS_CRE.objects.filter(det_pro = det_pro_cre).delete()
                xcod_cre = det_pro_cre.subcuenta
                DETALLE_PROD.objects.filter(hecho_econo = hecho_econo,subcuenta=xcod_cre).delete()
                resultado = (
                    DETALLE_PROD.objects.filter(
                        subcuenta = xcod_cre,
                        hecho_econo__docto_conta__oficina_id = 1
                    )
                    .aggregate(max_fecha=Max('hecho_econo__fecha'))
                )
                max_fecha = resultado['max_fecha'] or None
                xcre = CREDITOS.objects.filter(cod_cre = xcod_cre,oficina_id = 1).first()
                xcre.fec_ult_pag = max_fecha if max_fecha != None else xcre.fec_des
                xcre.estado = 'A'
                xcre.save()
            DETALLE_PROD.objects.filter(hecho_econo = hecho_econo).delete()
            hecho_econo.delete()
            return redirect('buscar_hechos_econo')
        
        return render(request, 'confirmar_eliminar_he.html', {'hecho_econo': hecho_econo,'errors': errors})
    return render(request, 'confirmar_eliminar_he.html', {'hecho_econo': hecho_econo})

#  aqui van las validaciones 

#  aqui van otros enpoint 
def buscar_hechos_econo(request,cliente_id=None, oficina_id=None, per_con=None):
    filtro_texto = request.GET.get('filtro_texto', '').strip()
    docto_conta_id = request.GET.get('docto_conta', None)
    fecha_inicio = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_fin', None)
    cliente_id = request.session.get('cliente_id')
    oficina_id = request.session.get('oficina_id')
    per_con = request.session.get('per_con')
    hechos_econo = HECHO_ECONO.objects.all()
    if len(filtro_texto) > 2:
        hechos_econo = hechos_econo.filter(descripcion__icontains=filtro_texto) | \
                        hechos_econo.filter(numero__icontains=filtro_texto)
    if docto_conta_id:
        hechos_econo = hechos_econo.filter(docto_conta_id=docto_conta_id)
    if fecha_inicio and fecha_fin:
        hechos_econo = hechos_econo.filter(fecha__range=[fecha_inicio, fecha_fin])
    # Obtener todas las opciones de docto_conta para el select
    docto_conta_options = DOCTO_CONTA.objects.filter(oficina_id = oficina_id,per_con = per_con)
    paginator = Paginator(hechos_econo, 10)  # muestra 10 registros por página
    page = request.GET.get('page')
    try:
        hechos_econo_pagina = paginator.page(page)
    except PageNotAnInteger:
        hechos_econo_pagina = paginator.page(1)
    except EmptyPage:
        hechos_econo_pagina = paginator.page(paginator.num_pages)
    context = {
        'hechos_econo': hechos_econo_pagina,
        'filtro_texto': filtro_texto,
        'docto_conta_id': docto_conta_id,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'docto_conta_options': docto_conta_options,  # opciones para el select
        'mostrar_resultados': len(filtro_texto) > 2 or docto_conta_id or (fecha_inicio and fecha_fin)
    }
    return render(request, 'hecho_econo_lista.html', context)

#  -------------------------------- r u t i n a s   g e n e r a l e s  ----------------------------------------
def causacion_credito(hecho,oficina_id, subcuenta):
    miCredito = CREDITOS.objects.filter(oficina_id=oficina_id, cod_cre=subcuenta).first()
    if miCredito is None:
        return JsonResponse({'success': False, 'error': f'Credito {subcuenta} No Existe'}, status=400)
    if miCredito.estado != 'X':
        return JsonResponse({'success': False, 'error': f'Credito {subcuenta} Ya Desembolsado'}, status=400)
    CREDITOS_CAUSA.objects.filter(cod_cre=subcuenta, comprobante_id=None).delete()
    xFecAnt = miCredito.fec_des
    xSaldo = miCredito.cap_ini
    xFecCuo = miCredito.fec_pag_ini
    iNumCuo = miCredito.num_cuo_ini
    iNumCuoGra = miCredito.num_cuo_gra
    xValCuo = miCredito.val_cuo_ini
    iFecPagIni = miCredito.fec_pag_ini
    xIntPorApl = 0
    xIntApl = 0
    iTIDIC = 0
    iTIDPS = 0
    xFecCuo = iFecPagIni
    per_ano = miCredito.per_ano
    iTIAN = miCredito.tian_ic_ini
    iTIEA = round(((1 + ((iTIAN / 12) / 100)) ** 12 - 1) * 100, 3)
    xTasIntPer = round((iTIEA / 100 + 1) ** (1 / per_ano) - 1, 6)
    iTIDIC = round(xTasIntPer * per_ano * 100 / 36525, 6)
    periodos = {12: 'M', 6: 'B', 4: 'T', 3: 'C', 2: 'B', 24: 'Q'}
    iPerio = periodos.get(per_ano, None)
    xMeses = per_ano / 12
    for xPer in range(1, iNumCuo + iNumCuoGra + 1):
        xDifDias = (xFecCuo - xFecAnt).days
        xIntIC = round(xSaldo * iTIDIC * 1000, 0)
        xIntIC = round(xIntIC / 1000, 0) * xDifDias
        xIntPS = round(xSaldo * iTIDPS * 1000, 0) * xDifDias
        xIntPS = round(xIntPS / 1000, 0) * xDifDias
        xIntPer = xIntIC + xIntPS + xIntPorApl
        xCapPer = round(xValCuo - xIntApl - xIntPer if xPer > iNumCuoGra and xValCuo - xIntApl - xIntPer > 0 else 0)
        xNueCapPer = xCapPer
        miCausa = CREDITOS_CAUSA.objects.create(
            oficina_id=oficina_id,
            comprobante_id=None,
            cuota=xPer,
            cod_cre=subcuenta,
            fecha=xFecCuo,
            capital=xCapPer if xPer < iNumCuo + iNumCuoGra else xSaldo,
            int_cor=xIntPer
        )
        miCausa.save()
        xIntApl = xIntApl + (xIntPer if xPer < iNumCuoGra else 0)
        xIntApl = xIntApl + (xValCuo - xNueCapPer - xIntPer if xIntPorApl > 0 else 0)
        xIntApl = xIntApl if xIntApl > 0 else 0
        xFecAnt = xFecCuo
        xSaldo = xSaldo - xCapPer
        if xMeses > 0:
            xFecCuo = gomonth(iFecPagIni, xMeses * xPer)
        elif iPerio == 'E':
            xFecCuo = xFecCuo + 7
        elif xPer % 2 == 1:
            xFecCuo = xFecCuo + 15
        else:
            xFecCuo = gomonth(xFecCuo - 15, 1)
    miCredito.estado='A'
    miCredito.fec_ult_pag = miCredito.fec_des
    miCredito.com_des_id = hecho
    miCredito.save()
    return JsonResponse({'success': True, 'message': f'Credito {subcuenta} procesado exitosamente'})


class ImprimePdf(View):
    locale.setlocale(locale.LC_TIME, 'Spanish_Spain') 
    def get(request, hecho_econo, pk, *args, **kwargs):
        hecho_Econo = HECHO_ECONO.objects.filter(id=pk).first()
        comprobante = DOCTO_CONTA.objects.filter(id=hecho_Econo.docto_conta_id).first()
        nombre_archivo = f"{comprobante.nombre.strip()}-{hecho_Econo.numero}.pdf"

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Configuración de márgenes y dimensiones
        width, height = letter
        margin_x = 50
        margin_y = 60
        line_height = 10
        max_lines_per_page = height - margin_y # 58 Ajusta según tu contenido
        y = margin_y

        # Función para dibujar texto con ajuste de línea
        def interlinear_texto(p, text, margin_x, y, max_width, line_height):
            max_chars_per_line = max_width // 6  # Aproximar caracteres por línea según fuente y tamaño
            lines = wrap(text, max_chars_per_line)

            for line in lines:
                p.drawString(margin_x, y, line)
                y -= line_height
            return y

        detalle_econos = DETALLE_ECONO.objects.filter(hecho_econo_id=pk).exclude(debito=0, credito=0)
        total_filas = len(detalle_econos)
        total_paginas = ceil(total_filas / max_lines_per_page) or 1
      
        # Variables para el número de página
        page_count = 1

        # Función para dibujar encabezado en cada página
        def dibujar_encabezado(page_count, total_paginas):
            # p.setFont("Courier-Bold", 15)
            entidad = CLIENTES.objects.filter(id=1).first()
            oficina = OFICINAS.objects.filter(id=1).first()
            p.setFont("Times-Roman", 12)
            p.drawString(width / 4, height - 30, f"{entidad.nombre}")
            p.drawString(width / 4, height - 45, f"NIT. {entidad.doc_ide}-{entidad.dv}")
            p.drawString(width / 4, height - 60, f"{oficina.nombre_oficina.upper()}")
            p.drawImage("hecho_economico_app\\Logo\\LOGO.jpg", margin_x - 10, height - margin_y - 40, 80, 80)

            # Información del Comprobante
            hecho_econo = HECHO_ECONO.objects.filter(id=pk).first()
            comprobante = DOCTO_CONTA.objects.filter(id=hecho_econo.docto_conta_id).first()
            p.drawString(width/2-30, height - margin_y - 20,f"{comprobante.nombre.strip()} No. {hecho_econo.numero}")
            # Agregar número de página en el encabezado
            p.setFont("Times-Roman", 10)
            p.drawString(width - margin_x - 25, height - margin_y - 20, f"Pág. {page_count} de {total_paginas}")

            # fecha_formateada = hecho_econo.fecha.strftime("%B %d de %Y").replace(" 0", " ")
            # canales = dict(OPC_CANALES)
            # canal_nombre = canales.get(hecho_econo.canal, "Canal Desconocido")
            # p.drawString(margin_x + 80, height - margin_y - 40,f"{oficina.ciudad.nombre.capitalize().strip()}, {fecha_formateada.capitalize()}     Canal: {canal_nombre}")
            
            # # p.drawString(margin_x + 300, height - margin_y - 40, f"Canal: {canal_nombre}")

            # p.drawString(margin_x + 450, height - margin_y - 40, f"$ {hecho_econo.valor:,.2f}")
            
            # # detalle_econos = DETALLE_ECONO.objects.filter(hecho_econo_id=pk).first()
            # # p.drawString(margin_x + 450, height - margin_y - 40, f"$ {detalle_econos.debito:,.2f}")
            
            # p.setFont("Times-Roman", 12)
            # # Datos principales
            # detalle_econos = DETALLE_ECONO.objects.filter(hecho_econo_id=pk).first()

            # # tercero = TERCEROS.objects.filter(doc_ide=hecho_econo.beneficiario).first()
            # tercero = TERCEROS.objects.filter(id=detalle_econos.tercero_id).first()
            # p.drawString(margin_x - 10, height - margin_y - 60, f"Beneficiario: {tercero.nombre.strip()}   NIT ó C.C. {tercero.doc_ide.strip()} DV. {tercero.dig_ver.strip()}")
            # detalles = DETALLE_PROD.objects.filter(hecho_econo_id=pk)
            # xConcepto = ''
            # for detalle in detalles:
            #     if detalle.producto == 'CR':
            #         MiCred = Liquida_cre(detalle.subcuenta,hecho_econo.fecha)
            #         MiCred.liq_al_dia(hecho_econo.fecha)
            #         saldo_capital = "{:,.2f}".format(float(MiCred.sal_cap_tot))
            #         xConcepto = xConcepto+'Crédito '+detalle.subcuenta+' Cuota '+str(MiCred.cuo_pag)+'/'+str(MiCred.cuo_pac)+' Saldo Cap. '+saldo_capital+'  '
              
       

            # print(xConcepto)
            # y = margin_y
            # xConcepto_formateado = f"Descripción: {xConcepto}"
            # y = interlinear_texto(p, xConcepto_formateado, margin_x-10, height - margin_y - 75, width, line_height)

            # # Dibujar valor en letras justo debajo
            # numero_en_letras = num2words(hecho_econo.valor, lang='es').upper()
            # num_let_formateado = f"SON: {numero_en_letras} PESOS M/CTE."
            # y = interlinear_texto(p, num_let_formateado, margin_x-10, y - 5, width, line_height)


# ***********************************************************
            # p.drawString(margin_x - 10, height - margin_y - 75, f"Descripción: {xConcepto}")
            # print( {tercero.nombre.strip()})

            # numero_en_letras = num2words(hecho_econo.valor, lang = 'es').upper()            
            # p.drawString(margin_x - 10, height - margin_y - 90, f"SON: {numero_en_letras} PESOS M/CTE.")
            # margin_x + 502


        # Función para dibujar pie de página
        def dibujar_pie():
            # Coordenadas para el inicio y fin de la línea
            line_y = margin_y - 30  # Ajusta para que esté justo encima del texto
            p.line(margin_x-40, line_y, margin_x + 552, line_y)  # Dibuja la línea
            p.setFont("Courier", 9)
            oficina = OFICINAS.objects.filter(id=1).first()
            texto_pie = f"{oficina.direccion.strip()}   Tel.: {oficina.celular.strip()}   e-mail: {oficina.email.strip()}   {oficina.ciudad.nombre.strip()}-{oficina.ciudad.departamento.strip()}"
            texto_ancho = stringWidth(texto_pie,"Courier", 9)
            p.drawString((width-texto_ancho)/2 , margin_y - 40, texto_pie)

        
        # Función para dibujar encabezado de la tabla de detalles
        def dibujar_encabezado_tabla(y):
            # Definir el margen izquierdo y la altura del encabezado
            header_height = 15  # Altura del fondo del encabezado
            # Dibujar rectángulos de fondo
            p.setFillColorRGB(0.8, 0.8, 0.8)  # Color de fondo (gris claro)
            p.rect(margin_x - 10, y - header_height + 5, 80,header_height, fill=1)  # Fondo para "Código"
            p.rect(margin_x + 35, y - header_height + 5, 225,header_height, fill=1)  # Fondo para "Cuenta"
            p.rect(margin_x + 195, y - header_height + 5, 220,header_height, fill=1)  # Fondo para "Detalle"
            p.rect(margin_x + 400, y - header_height + 5, 70,header_height, fill=1)  # Fondo para "Débito"
            p.rect(margin_x + 470, y - header_height + 5, 70,header_height, fill=1)  # Fondo para "Crédito"

            # Dibujar el texto de los encabezados
            p.setFillColorRGB(0, 0, 0)  # Color del texto (negro)
            p.setFont("Times-Bold", 11)
            p.drawString(margin_x - 5, y-5, "Código")
            p.drawString(margin_x + 40, y-5, "Cuenta")
            p.drawString(margin_x + 200, y-5, "Tercero")
            p.drawString(margin_x + 300, y-5, "Detalle")
            p.drawString(margin_x + 420, y-5, "Débito")
            p.drawString(margin_x + 485, y-5, "Crédito")


        # Dibujar encabezado principal de la primera página
        hecho_econo = HECHO_ECONO.objects.filter(id=pk).first()
        oficina = OFICINAS.objects.filter(id=1).first()
        p.setFont("Times-Roman", 10)
        fecha_formateada = hecho_econo.fecha.strftime("%B %d de %Y").replace(" 0", " ")
        canales = dict(OPC_CANALES)
        canal_nombre = canales.get(hecho_econo.canal, "Canal Desconocido")
        p.drawString(margin_x + 80, height - margin_y - 40,f"{oficina.ciudad.nombre.capitalize().strip()}, {fecha_formateada.capitalize()}     Canal:{canal_nombre}")

        p.drawString(margin_x + 450, height - margin_y - 40, f"$ {hecho_econo.valor:,.2f}")
            
        p.setFont("Times-Roman", 11)
        # Datos principales
        detalle_econos = DETALLE_ECONO.objects.filter(hecho_econo_id=pk).first()
        tercero = TERCEROS.objects.filter(id=detalle_econos.tercero_id).first()
        p.drawString(margin_x - 10, height - margin_y - 60, f"Beneficiario: {tercero.nombre.strip()}   NIT ó C.C. {tercero.doc_ide.strip()} DV. {tercero.dig_ver.strip()}")
        # Descripción detallada del movimiento
        detalles = DETALLE_PROD.objects.filter(hecho_econo_id=pk)
        xConcepto = ''
        for detalle in detalles:
            if detalle.producto == 'CR':
                if detalle.concepto == 'DESEM':
                    MiCred = Liquida_cre(detalle.subcuenta,hecho_econo.fecha)
                    MiCred.liq_al_dia(hecho_econo.fecha)
                    saldo_capital = "{:,.2f}".format(float(MiCred.sal_cap_tot))
                    xConcepto = xConcepto+' '+detalle.concepto+' Crédito '+detalle.subcuenta+' Capital '+saldo_capital+'  '
                else:    
                    MiCred = Liquida_cre(detalle.subcuenta,hecho_econo.fecha)
                    MiCred.liq_al_dia(hecho_econo.fecha)
                    saldo_capital = "{:,.2f}".format(float(MiCred.sal_cap_tot))
                    xConcepto = xConcepto+'Crédito '+detalle.subcuenta+' Cuota '+str(MiCred.cuo_pag)+'/'+str(MiCred.cuo_pac)+' Saldo Cap. '+saldo_capital+'  '
            
            elif detalle.producto == 'AP':
                xConcepto = xConcepto+detalle.concepto+' '+detalle.subcuenta+'  '

            elif detalle.producto == 'AH':
                xConcepto = xConcepto+detalle.concepto+' '+detalle.subcuenta+'  '

            elif detalle.producto == 'OT':
                xConcepto = xConcepto+detalle.concepto+' '+detalle.subcuenta+'  '
            
            # else:                
        
        print(xConcepto)

        y = margin_y
        xConcepto_formateado = f"Descripción: {xConcepto}"
        y = interlinear_texto(p, xConcepto_formateado, margin_x-10, height - margin_y - 75, width, 12)
       
        descripcion = len(xConcepto_formateado)

        print(descripcion)

        # Dibujar valor en letras justo debajo
        pesos = ''
        if hecho_econo.valor == 0:
            pesos = 'PESOS M/CTE.'
        elif hecho_econo.valor % 1_000_000 == 0:
            pesos = 'DE PESOS M/CTE.'
        else:
            pesos = 'PESOS M/CTE.'

        numero_en_letras = num2words(hecho_econo.valor, lang='es').upper()
        num_let_formateado = f"SON: {numero_en_letras} {pesos}"
        y = interlinear_texto(p, num_let_formateado, margin_x-10, y - 5, width, 12)    
       

        # Generar detalles de comprobante
        detalle_econos = DETALLE_ECONO.objects.filter(hecho_econo_id=pk).exclude(debito=0, credito=0)

        # y = height - margin_y - 120  # Posición inicial para detalles
       
        line_count = 0
        page_count = 1

        # Generar cada línea del detalle con paginación
        for idx, det_eco in enumerate(detalle_econos, start=1):
            if idx % max_lines_per_page == 1:  # Nueva página
                if idx > 1:
                    dibujar_pie()
                    p.showPage()
                    page_count += 1
                dibujar_encabezado(page_count, total_paginas)
                # y = y - 5
                # y = height - 110
                dibujar_encabezado_tabla(y)
                y -= line_height
                line_count = 0  # Reiniciar el contador de líneas en la nueva página

            # Dibujar los datos del detalle
            cta_con = PLAN_CTAS.objects.filter(id=det_eco.cuenta_id).first()
            ter_det = TERCEROS.objects.filter(id=det_eco.tercero_id).first()
            p.setFont("Times-Roman", 10)
            p.drawString(margin_x - 10, y-10, f"{cta_con.cod_cta}")
            p.drawString(margin_x + 40, y-10, f"{cta_con.nom_cta[:24]}")
            # p.drawString(margin_x + 300, y-10,f"{det_eco.detalle[:35]}")
            p.drawString(margin_x + 200, y-10,f"{ter_det.doc_ide[:12]} {ter_det.nombre[:23]}")
            p.drawRightString(margin_x + 470, y-10, f"{det_eco.debito:,.2f}")
            p.drawRightString(margin_x + 540, y-10, f"{det_eco.credito:,.2f}")
            y -= line_height
            line_count += 1


        # Resumen al final
        p.setFont("Times-Roman", 10)
        p.line(margin_x + 400, y - 5, margin_x + 472, y - 5)
        p.line(margin_x + 472, y - 5, margin_x + 542, y - 5)
        p.drawString(margin_x - 10, y - 25, "Resumen del Comprobante")
        p.drawString(margin_x + 250, y - 25, f"Total Débitos:")
        p.drawString(margin_x + 250, y - 40, f"Total Créditos:")
        p.drawRightString(margin_x + 470, y - 25, f"{sum([det.debito for det in detalle_econos]):,.2f}")
        p.line(margin_x + 400, y - 27, margin_x + 472, y - 27)
        p.line(margin_x + 400, y - 29, margin_x + 472, y - 29)
        p.drawRightString(margin_x + 540, y - 40, f"{sum([det.credito for det in detalle_econos]):,.2f}")
        p.line(margin_x + 472, y - 42, margin_x + 542, y - 42)
        p.line(margin_x + 472, y - 44, margin_x + 542, y - 44)

        entidad = CLIENTES.objects.filter(id=1).first()
        user = User.objects.filter(id=hecho_econo.user_id).first()
        usuario = user.username
        hora_actual = datetime.now().strftime("%H:%M:%S")
        canales = dict(OPC_CANALES)
        canal_nombre = canales.get(hecho_Econo.canal, "Canal Desconocido")
        referencia = hecho_Econo.cheque if hecho_Econo.cheque is not None else ""
        banco = hecho_Econo.banco if hecho_Econo.banco is not None else ""
        
        if comprobante.codigo == 1:
            # Cuadro de firma
            p.setFont("Times-Roman", 9)
            p.drawString(margin_x, y - 70, f"FORMA DE PAGO: {canal_nombre}   REF. {referencia}   BANCO: {banco}")
            p.drawString(margin_x, y - 80, f"OBSERVACIONES: {hecho_Econo.descripcion.upper()}")
            p.drawString(margin_x, y - 115, "USUARIO: ")
            p.drawString(margin_x + 45, y - 115, f"{usuario}  {hora_actual}")
            p.line(margin_x + 390, y - 105, margin_x + 530, y - 105)
            p.drawString(margin_x + 445, y - 115, "RECIBÍ")
            p.line(margin_x + 380, y - 120, margin_x + 380, y - 60)
            p.roundRect(margin_x - 10, y - 120, margin_x + 502, 60, 8)  # Cuadro de firma

        elif comprobante.codigo == 2:
            # Cuadro de firma
            p.setFont("Times-Roman", 9)
            p.drawString(margin_x + 325, y - 70, "Firma y sello del beneficiario ")
            p.setFont("Times-Roman", 9)
            p.drawString(margin_x, y - 70, f"FORMA DE PAGO: {canal_nombre}   REF. {referencia}   BANCO: {banco}")
            p.drawString(margin_x, y - 80, f"OBSERVACIONES: {hecho_Econo.descripcion.upper()}")
            
            p.line(margin_x-10, y - 95, margin_x + 320, y - 95)
            p.drawString(margin_x, y - 105, "Elaborado")
            p.drawString(margin_x, y - 115, f"{usuario}  {hora_actual}")

            p.line(margin_x + 105, y - 95, margin_x + 105, y - 120)
            p.drawString(margin_x + 110, y - 105, "Revisado")
            p.drawString(margin_x + 110, y - 115, f"{entidad.nom_con[:22]}")
            
            p.line(margin_x + 210, y - 95, margin_x + 210, y - 120)
            p.drawString(margin_x + 215, y - 105, "Aprobado")
            p.drawString(margin_x + 215, y - 115, f"{entidad.nom_ger[:22]}")

            p.setFont("Times-Roman", 9)
            p.line(margin_x + 320, y - 105, margin_x + 542, y - 105)
            p.drawString(margin_x + 325, y - 115, "C.C.       NIT.       No.")
            p.rect(margin_x + 345, y - 116, 10, 8)
            p.rect(margin_x + 377, y - 116, 10, 8)
            p.line(margin_x + 320, y - 120, margin_x + 320, y - 60)
            p.roundRect(margin_x - 10, y - 120, margin_x + 502, 60, 8)  # Cuadro de firma
        else:
            # Cuadro de firma
            p.setFont("Times-Roman", 9)
            p.drawString(margin_x, y - 70, f"FORMA DE PAGO: {canal_nombre}   REF. {referencia}   BANCO: {banco}")
            p.drawString(margin_x, y - 80, f"OBSERVACIONES: {hecho_Econo.descripcion.upper()}")
            # p.drawString()
            p.line(margin_x-10, y - 95, margin_x + 542, y - 95)
            p.drawString(margin_x, y - 105, "Elaborado")
            p.drawString(margin_x, y - 115, f"{usuario}  {hora_actual}")

            p.line(margin_x + 165, y - 95, margin_x + 165, y - 120)
            p.drawString(margin_x + 170, y - 105, "Revisado")
            p.drawString(margin_x + 170, y - 115, f"{entidad.nom_con[:30]}")

            p.line(margin_x + 360, y - 95, margin_x + 360, y - 120)
            p.drawString(margin_x + 365, y - 105, "Aprobado")
            p.drawString(margin_x + 365, y - 115, f"{entidad.nom_ger[:30]}")

            p.roundRect(margin_x - 10, y - 120, margin_x + 502, 60, 8)  # Cuadro de firma
               
        total_paginas = page_count

        # Dibuja el pie de página
        dibujar_pie()
        
        p.showPage()
        p.save()
        buffer.seek(0)
        response.write(buffer.read())
        buffer.close()
        return response