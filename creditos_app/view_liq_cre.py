from django.shortcuts import render
from django.http import HttpResponse
from .models import CREDITOS
from justo_app.justo_creditos import Liquida_cre  # Asegúrate de importar tu clase de liquidación
from django.http import HttpResponse, JsonResponse
import os
import pandas as pd
from datetime import datetime


def liquidar_creditos(request):
    if request.method == 'POST':
        fecha_corte_str = request.POST.get('fecha_corte')
        nombre_archivo = request.POST.get('nombre_archivo')
        try:
            total_creditos = liquidar_creditos_process(fecha_corte_str, nombre_archivo, request)
            return JsonResponse({'message': 'Cálculos de liquidación iniciados.'})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return render(request, 'liquidacion.html')

from django.db.models import Q

def liquidar_creditos_process(fecha_corte_str, nombre_archivo, request):
    print('Hora de Inicio .... ',datetime.now())
    # Convertir la cadena de fecha a un objeto datetime.date
    fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
    
    # Verifica si el directorio del archivo existe
    if not os.path.exists(os.path.dirname(nombre_archivo)):
        raise ValueError("El directorio especificado no existe.")
    creditos = CREDITOS.objects.filter(oficina_id=1).exclude(Q(estado='C', fec_ult_pag__lt=fecha_corte) | Q(fec_des__gt=fecha_corte)) 
    total_creditos = creditos.count()
    resultados = []
    for index, credito in enumerate(creditos):
        liquidacion = Liquida_cre(credito.cod_cre, fecha_corte)
        if liquidacion.lista_mov is None:
           # print('Problemas Credito ', liquidacion.cod_cre)
            continue
        liquidacion.liq_al_dia(fecha_corte)
        if liquidacion.sal_cap_tot > 0 :
            # print('Hora  ',datetime.now(),'    Credito ',credito.cod_cre,'   Saldo Cap  ',liquidacion.sal_cap_tot)
            resultados.append({
                'cod_cre': liquidacion.cod_cre,
                'cap_ini': liquidacion.cap_ini,
                'fecha_focal': liquidacion.fecha_focal,
                'val_cuo': liquidacion.val_cuo,
                'fec_des': liquidacion.fec_des,
                'for_pag': liquidacion.for_pag,
                'sal_cap_tot': liquidacion.sal_cap_tot,
                'sal_cap_dia': liquidacion.sal_cap_dia,
                'sal_int_dia': liquidacion.sal_int_dia,
                'sal_ps_dia': liquidacion.sal_ps_dia,
                'sal_int_mor': liquidacion.sal_int_mor,
                'int_cau_fra': liquidacion.int_cau_fra,
                'int_aju_pa': liquidacion.int_aju_pa,
                'int_pag_tot': liquidacion.int_pag_tot,
                'altura': liquidacion.altura,
                'cuo_pag': liquidacion.cuo_pag,
                'cuo_pac': liquidacion.cuo_pac,
                'fec_al_dia': liquidacion.fec_al_dia,
                'fec_ven': liquidacion.fec_ven,
                'tas_ic_ea': liquidacion.tas_ic_ea,
                'tas_ic_dia': liquidacion.tas_ic_dia,
                'tas_im_anual': liquidacion.tas_im_anual,
                'por_des_pp': liquidacion.por_des_pp,
                'per_ano': liquidacion.per_ano,
                'tip_pag': liquidacion.tip_pag,
                'capital_a_pag': liquidacion.capital_a_pag,
                'int_cor_a_pag': liquidacion.int_cor_a_pag,
                'pol_seg_a_pag': liquidacion.pol_seg_a_pag,
                'int_mor_a_pag': liquidacion.int_mor_a_pag,
                'acreedor_a_pag': liquidacion.acreedor_a_pag,
                'int_mor_cau': liquidacion.int_mor_cau,
                'aju_cap_a_pag': liquidacion.aju_cap_a_pag,
                'aju_ic_a_pag': liquidacion.aju_ic_a_pag,
                'aju_ps_a_pag': liquidacion.aju_ps_a_pag,
                'aju_im_a_pag': liquidacion.aju_im_a_pag,
                'max_pag_couta': liquidacion.max_pag_couta,
                'min_pag_aboca': liquidacion.min_pag_aboca,
                'min_pag_abocu': liquidacion.min_pag_abocu,
                'fec_sig_pag1': liquidacion.fec_sig_pag1,
                'fec_sig_pag2': liquidacion.fec_sig_pag2,
                'tip_pag': liquidacion.tip_pag,
                'int_pag_per': liquidacion.int_pag_per,
                'int_condo': liquidacion.int_condo
            })
        # Llamar al callback de progreso
        # update_progress(int((index + 1) / total_creditos * 100), request)
    print('Hora de Terminacion ',datetime.now())  
        
    # Crear un DataFrame de pandas con los resultados
    df = pd.DataFrame(resultados)
    
    # Guardar el DataFrame en un archivo Excel
    df.to_excel(nombre_archivo, index=False)
    
    return total_creditos

def update_progress(progress, request):
    # Esta función podría ser utilizada para enviar actualizaciones de progreso en tiempo real a través de WebSockets o similar
    request.session['progress'] = progress

def get_progress(request):
    # Simular progreso
    progress = 50  # Ejemplo de progreso, ajusta según lo que necesites
    return JsonResponse({'progress': progress})

from django.shortcuts import render, get_object_or_404

def liquidacion_justo(request,pk):
    Credito = get_object_or_404(CREDITOS, pk=pk)
    print('Credito ',Credito.cod_cre)
    if request.method == 'POST':
        print('Entra a post')
        cod_cre = request.POST.get('codigo_credito')
        fecha_liquidacion_str = request.POST.get('fecha_liquidacion')
        tipo_pago = request.POST.get('tipo_pago')
        numero_cuotas = request.POST.get('numero_cuotas')
        valor_pago = request.POST.get('valor_pago')
        resultado = ''
        if Credito == None:
            resultado = 'Codigo del Credito No existe'
            return JsonResponse({'error': resultado})
        if Credito.estado == 'C':
            resultado = 'Este Credito ya esta Cancelado'
            return JsonResponse({'error': resultado})
        fecha_liquidacion = datetime.strptime(fecha_liquidacion_str, '%Y-%m-%d').date()
        liq_cre = Liquida_cre(cod_cre,fecha_liquidacion)
        if tipo_pago == 'pago_al_dia':
            liq_cre.liq_al_dia(fecha_liquidacion)
        elif tipo_pago == 'pago_por_cuotas':
            liq_cre.liq_por_cuotas(liq_cre.cuo_pag+int(numero_cuotas))
        elif tipo_pago == 'pago_por_valor':
            liq_cre.distri_pago_cuota(float(valor_pago))
        elif tipo_pago == 'abono_a_capital':
            liq_cre.distri_pago_abo(float(valor_pago))
        elif tipo_pago == 'pago_total':
            liq_cre.liq_al_dia(fecha_liquidacion)

        if tipo_pago == 'pago_total':
            print('Opcion ',tipo_pago)
            print('sal_int_dia -',liq_cre.sal_int_dia)
            print('int_cau_fra  ',liq_cre.int_cau_fra)
            print('int_aju_pa   ',liq_cre.int_aju_pa)
            print('int_pag_tot  ',liq_cre.int_pag_tot)
            print('int_cor_a_pag',liq_cre.int_cor_a_pag)
            print('aju_ic_a_pag  ',liq_cre.aju_ic_a_pag)
            resultado = {
                'cap_a_pag': liq_cre.sal_cap_tot,
                'capital': liq_cre.capital_a_pag,  
                'cap_aju': 0,
                'ic_a_pag': liq_cre.sal_int_dia + liq_cre.int_cau_fra - liq_cre.aju_ic_a_pag,
                'int_cor': liq_cre.sal_int_dia,
                'ic_aju': liq_cre.int_cau_fra,
                'im_a_pag': liq_cre.int_mor_a_pag,
                'int_mor': liq_cre.sal_int_mor,
                'im_aju': liq_cre.aju_im_a_pag,
                'ps_a_pag': liq_cre.pol_seg_a_pag,
                'pol_seg': liq_cre.pol_seg_a_pag,
                'ps_aju': liq_cre.aju_ps_a_pag,
                'acreedores': liq_cre.acreedor_a_pag,
                'total_a_pagar': liq_cre.sal_cap_tot+liq_cre.sal_int_dia + liq_cre.int_cau_fra + liq_cre.int_mor_a_pag+liq_cre.pol_seg_a_pag+liq_cre.acreedor_a_pag,
                'tot_cap_pagado' : liq_cre.cap_ini - liq_cre.sal_cap_tot,
                'tot_cap_x_pag' : liq_cre.sal_cap_tot-liq_cre.sal_cap_tot,
                'tot_cap_liq' : liq_cre.sal_cap_tot
            }
        else: 
            if tipo_pago == 'pago_al_dia' and liq_cre.sal_cap_dia<0:
                resultado = {
                    'cap_a_pag': 0,
                    'capital': 0,  
                    'cap_aju': 0,
                    'ic_a_pag': 0,
                    'int_cor': 0,
                    'ic_aju': 0,
                    'im_a_pag': 0,
                    'int_mor': 0,
                    'im_aju': 0,
                    'ps_a_pag': 0,
                    'pol_seg': 0,
                    'ps_aju': 0,
                    'acreedores': 0,
                    'total_a_pagar': 0,
                    'tot_cap_pagado' : 0,
                    'tot_cap_x_pag' : 0,
                    'tot_cap_liq' : 0
                }
            else:
                resultado = {
                    'cap_a_pag': liq_cre.capital_a_pag,
                    'capital': liq_cre.capital_a_pag,  
                    'cap_aju': liq_cre.aju_cap_a_pag,
                    'ic_a_pag': liq_cre.int_cor_a_pag,
                    'int_cor': liq_cre.int_cor_a_pag - liq_cre.aju_ic_a_pag,
                    'ic_aju': liq_cre.aju_ic_a_pag,
                    'im_a_pag': liq_cre.int_mor_a_pag,
                    'int_mor': liq_cre.sal_int_mor,
                    'im_aju': liq_cre.aju_im_a_pag,
                    'ps_a_pag': liq_cre.pol_seg_a_pag,
                    'pol_seg': liq_cre.pol_seg_a_pag,
                    'ps_aju': liq_cre.aju_ps_a_pag,
                    'acreedores': liq_cre.acreedor_a_pag,
                    'total_a_pagar': liq_cre.capital_a_pag+liq_cre.int_cor_a_pag+liq_cre.int_mor_a_pag+liq_cre.pol_seg_a_pag+liq_cre.acreedor_a_pag,
                    'tot_cap_pagado' : liq_cre.cap_ini - liq_cre.sal_cap_tot,
                    'tot_cap_x_pag' : liq_cre.sal_cap_tot-liq_cre.capital_a_pag,
                    'tot_cap_liq' : liq_cre.capital_a_pag
                }
        return JsonResponse({'resultado': resultado})

    return render(request, 'liquidacion_justo.html', {'credito': Credito})


from django.shortcuts import render
from django.core.paginator import Paginator
from django.db import connection

def consulta_detalle_prod(request, subcuenta):
    credito = CREDITOS.objects.filter(oficina=1,cod_cre = subcuenta).first()
    query = """
    SELECT 
        hecho_econo.fecha AS fecha,
        docto_conta.nom_cto,
        hecho_econo.numero,
        detalle_prod.concepto,
        -detalle_prod.valor AS Pagado,
        COALESCE(SUM(CASE WHEN detalle_econo.item_concepto = 'Kapita' THEN ((detalle_econo.valor_2) - detalle_econo.valor_1) ELSE NULL END), 0.0) AS kapital,
        COALESCE(SUM(CASE WHEN detalle_econo.item_concepto = 'IntCor' THEN ((detalle_econo.valor_2) - detalle_econo.valor_1) ELSE NULL END), 0.0) AS intcor,
        COALESCE(SUM(CASE WHEN detalle_econo.item_concepto = 'IntMor' THEN ((detalle_econo.valor_2) - detalle_econo.valor_1) ELSE NULL END), 0.0) AS intmot,
        COALESCE(SUM(CASE WHEN detalle_econo.item_concepto = 'PolSeg' THEN ((detalle_econo.valor_2) - detalle_econo.valor_1) ELSE NULL END), 0.0) AS polseg,
        COALESCE(SUM(CASE WHEN detalle_econo.item_concepto = 'DesPP' THEN ((detalle_econo.valor_2) - detalle_econo.valor_1) ELSE NULL END), 0.0) AS despp,
        COALESCE(SUM(CASE WHEN detalle_econo.item_concepto = 'Acreed' THEN ((detalle_econo.valor_2) - detalle_econo.valor_1) ELSE NULL END), 0.0) AS acreed,
        0.00 AS Saldo_cap
    FROM 
        detalle_prod 
    INNER JOIN 
        hecho_econo ON (detalle_prod.hecho_econo_id = hecho_econo.id) 
    INNER JOIN 
        docto_conta ON (docto_conta.id = hecho_econo.docto_conta_id)
    LEFT OUTER JOIN 
        detalle_econo ON (detalle_prod.id = detalle_econo.detalle_prod_id) 
    WHERE 
        (detalle_prod.oficina_id = 1 and detalle_prod.producto = 'CR' AND detalle_prod.subcuenta = %s)
    GROUP BY 
        hecho_econo.fecha, docto_conta.nom_cto, hecho_econo.numero, detalle_prod.concepto
    ORDER BY 
        hecho_econo.fecha ;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [subcuenta])
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        saldo_cap = credito.cap_ini
        rows = []
        totals = [0.0] * (len(columns) - 1)
        for row in results:
            if row[4] != 'DESEM':
                saldo_cap -= float(row[5])
            updated_row = list(row)
            updated_row[11] = saldo_cap  # Actualiza el índice 11
            formatted_row = [
                f"{val:,.2f}" if isinstance(val, float) else val
                for val in updated_row
            ]
            rows.append(formatted_row)
            for i in range(4, len(totals)-1):  # Acumulamos totales, excluyendo la primera columna
                if isinstance(updated_row[i], float):
                    if row[4] != 'DESEM':
                        totals[i - 1] += updated_row[i]
        totals_row = ["Total"] + [f"{total:,.2f}" for total in totals] + [""]
        rows.append(totals_row)

    paginator = Paginator(rows, 16)  # 10 resultados por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'columns': columns,
        'page_obj': page_obj,
        'subcuenta': subcuenta,
        'credito' : credito
    }

    return render(request, 'lista_mov_creditos.html', context)


