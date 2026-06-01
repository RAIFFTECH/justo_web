import csv, os
from django.db import connection
from django.utils.timezone import make_aware
import pandas as pd
from openpyxl import Workbook
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from math import ceil
from reportlab.lib.pagesizes import landscape, letter, legal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.db import models
from django.db.models import Sum, Max, Min, Value, FloatField, IntegerField, DateField, Case, When, F, DecimalField, Count, ExpressionWrapper, Subquery, OuterRef, Q
from django.db.models.functions import Cast, Coalesce, Now, ExtractYear, ExtractMonth, TruncDate, ExtractDay
from django.core.paginator import Paginator
from datetime import date, timedelta, datetime
from itertools import chain
from django import forms

from .forms import CrearForm
from .models import PLAN_APORTES
from clientes_app.models import CLIENTES
from oficinas_app.models import OFICINAS
from asociados_app.models import ASOCIADOS
from terceros_app.models import TERCEROS
from detalle_producto_app.models import DETALLE_PROD
from hecho_economico_app.models import HECHO_ECONO
from creditos_app.models import CREDITOS
from estados_financieros_app.models import ESTADOS_FIN
from localidades_app.models import LOCALIDADES
from recla_carte_app.models import CARTE_CAT_HIS
from justo_app.opciones import OPC_EST_SOCIO, OPC_EDUCACION, OPC_EST_CIV
from justo_app.views import formato_fecha
# Para obtener todos los registros
class Lista(LoginRequiredMixin, ListView):
    model = PLAN_APORTES
    form = CrearForm
    template_name = 'lista_aportes.html'
    # ordering = ['cliente','per_con','cod_cta']

# Para obtener todos los detalles de un registro
class Detalles(LoginRequiredMixin, DetailView):
    model = PLAN_APORTES
    form = CrearForm
    template_name = 'detalles_aporte.html'

# Para crear un nuevo registro
class Crear(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = PLAN_APORTES
    form = CrearForm
    fields = '__all__'
    template_name = 'crear_aporte.html'

    # Mensaje que se mostrará cuando se inserte el registro
    success_message = 'Registro añadido correctamente.'

    # Redirigimos a la página principal tras insertar el registro
    def get_success_url(self):
        return reverse('listar_aporte')

# Para modificar un registro
class Actualizar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = PLAN_APORTES
    form = CrearForm
    fields = '__all__'
    template_name = 'actualizar_aporte.html'
    # Mensaje que se mostrará cuando se actualice el registro
    success_message = 'Registro actualizado correctamente.'

    # Redireccionamos a la página principal tras actualizar el registro
    def get_success_url(self):
        return reverse('listar_aporte')

# Para eliminar un registro
class Eliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = PLAN_APORTES
    form = CrearForm
    fields = "__all__"

    # Redireccionamos a la página principal tras de eliminar el registro
    def get_success_url(self):
        # Mensaje que se mostrará cuando se elimine el registro
        success_message = 'Registro eliminado correctamente.'
        messages.success(self.request, (success_message))
        return reverse('listar_aporte')

# Primera consulta: Saldo Anterior
def ejecutar_consulta_orm(oficina_id,subcuenta,fecha_ini,fecha_fin):
    # Primera parte de la consulta
    saldo_anterior = DETALLE_PROD.objects.filter(
        producto = 'AP',
        subcuenta = subcuenta,
        hecho_econo__fecha__lt = fecha_ini - timedelta(days = 1),
        hecho_econo__docto_conta__oficina_id=oficina_id
    ).aggregate(
        Saldo=Coalesce(-Sum('valor'), 0, output_field=FloatField())
    )
    resultado_saldo_anterior = {
        'Fecha' : fecha_ini - timedelta(days = 1),
        'Comprobante' : 'Saldo Anterior',
        'Numero' : 0,
        'Concepto': '',
        'Aporte' : 0,
        'Retiro' : 0,
        'Saldo' : saldo_anterior['Saldo']
    }
    
    # Segunda parte de la consulta
    movimientos = DETALLE_PROD.objects.filter(
        producto='AP',
        subcuenta=subcuenta,
        hecho_econo__fecha__range=(fecha_ini, fecha_fin),
        hecho_econo__docto_conta__oficina_id=oficina_id
    ).annotate(
        Fecha=F('hecho_econo__fecha'),
        Comprobante=F('hecho_econo__docto_conta__nombre'),
        Numero=F('hecho_econo__numero'),
        Concepto=F('concepto'),
        Aporte=Case(
            When(valor__lt=0, then=-F('valor')),
            default=Value(0),
            output_field=FloatField()
        ),
        Retiro=Case(
            When(valor__gt=0, then=F('valor')),
            default=Value(0),
            output_field=FloatField()
        ),
        Saldo=Value(0, output_field=FloatField())
    ).values(
        'Fecha', 'Comprobante', 'Numero', 'Concepto', 'Aporte', 'Retiro', 'Saldo'
    ).order_by('Fecha')

    # Unir las dos partes
    resultados = [resultado_saldo_anterior] + list(movimientos)    
    return resultados

def movtos_aporte_socio(request, cliente_id=None, oficina_id=None):
    if request.method == 'GET':
        # return render(request, 'movtos_apo_soc.html')
    # if request.method == 'POST':
        accion = request.GET.get("accion")  # Obtener la acción
        id_cli = request.session.get('cliente_id')
        id_ofi = request.session.get('oficina_id')
        filtro_socio = request.GET.get('filtro_cod_socio', '').strip()
        fecha_ini = request.GET.get('fecha_inicio', None)
        fecha_fin = request.GET.get('fecha_final', None)
        print('Filtro  ',filtro_socio,'    fecha_ini ',fecha_ini,'   fecha_fin ',fecha_fin)
        oficina_id = request.session.get('oficina_id')
        date_format = "%Y-%m-%d"
        fecha_actual = datetime.now()
        if fecha_ini == None:
            fecha_inicio = datetime(fecha_actual.year - 1, 1, 1).date()
        else:
            fecha_inicio = datetime.strptime(fecha_ini, date_format).date()
        if fecha_fin == None:
            fecha_final = datetime(fecha_actual.year - 1, 1, 1).date()
        else:
            fecha_final = datetime.strptime(fecha_fin, date_format).date()
        fecha_final = fecha_actual.date()
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_final_str = fecha_final.strftime('%Y-%m-%d')
        oficina_id = int(request.GET.get('oficina_id', 1))  # Obtiene el valor de oficina_id de los parámetros GET
        if len(filtro_socio) > 3: 
            resultados = ejecutar_consulta_orm(oficina_id,filtro_socio,fecha_inicio,fecha_final)
        else:
            resultados = []
        rows = []
        sal_acu = 0
        for row in resultados:
            sal_acu = sal_acu + float(row['Aporte']) - float(row['Retiro']) + float(row['Saldo'])
            upd_row = row
            upd_row['Saldo'] = sal_acu
            rows.append(upd_row)

        print(resultados)

        paginator = Paginator(rows, 10)  # 10 resultados por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if accion == "exportar":
            return exportar(request, rows)
        elif accion == "csv":
            return exportar_csv(request, rows)
        elif accion == 'imprimir':
            return imprimir(request, rows)

        return render(request, 'movtos_apo_soc.html', {
            'context': page_obj,
            'page_obj': page_obj,
            'filtro_cod_socio' : filtro_socio,
            'fecha_inicio': fecha_inicio_str,
            'fecha_final': fecha_final_str
        })
    return HttpResponse("Método no permitido", status=405)

def exportar(request, rows):
    id_cli = request.session.get('cliente_id')
    id_ofi = request.session.get('oficina_id')
    filtro_socio = request.GET.get('filtro_cod_socio', '').strip()
    fecha_ini = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_final', None)
    print('Filtro  ',filtro_socio,'    fecha_ini ',fecha_ini,'   fecha_fin ',fecha_fin)
    oficina_id = request.session.get('oficina_id')
    date_format = "%Y-%m-%d"
    fecha_actual = datetime.now()
    if fecha_ini == None:
        fecha_inicio = datetime(fecha_actual.year - 1, 1, 1).date()
    else:
        fecha_inicio = datetime.strptime(fecha_ini, date_format).date()
    if fecha_fin == None:
        fecha_final = datetime(fecha_actual.year - 1, 1, 1).date()
    else:
        fecha_final = datetime.strptime(fecha_fin, date_format).date()
    fecha_final = fecha_actual.date()
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_final_str = fecha_final.strftime('%Y-%m-%d')
    oficina_id = int(request.GET.get('oficina_id', 1))
  
    # Lógica para exportar Crear el libro de Excel
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Movimiento Aportes" 

    entidad = CLIENTES.objects.filter(id=id_cli).first()
    oficina = OFICINAS.objects.filter(id=id_ofi).first()
    tercero = TERCEROS.objects.filter(doc_ide=filtro_socio).first()

    # Llama a la función para obtener los datos
    resultados = ejecutar_consulta_orm(oficina_id,filtro_socio,fecha_inicio,fecha_final)

    if len(filtro_socio) > 3: 
        resultados = ejecutar_consulta_orm(oficina_id,filtro_socio,fecha_inicio,fecha_final)
    else:
        resultados = []
    rows = []
    sal_acu = 0
    for row in resultados:
        sal_acu = sal_acu + float(row['Aporte']) - float(row['Retiro']) + float(row['Saldo'])
        upd_row = row
        upd_row['Saldo'] = sal_acu
        rows.append(upd_row)
                    
    if not resultados:
        return HttpResponse("No se encontraron datos para exportar", status=404)
    
    fecha_inicio_formateada = formato_fecha(fecha_inicio)
    fecha_final_formateada = formato_fecha(fecha_final)
                        
    # Añadir datos adicionales encima de los encabezados
    empresa = f"{entidad.nombre.strip()}"
    nit_empresa = f"NIT. {entidad.doc_ide.strip()}-{entidad.dv.strip()}"
    reporte = "MOVIMIENTO DE APORTES "
    asociado = f"Asociado: {filtro_socio} {tercero.nombre}"
    detalles = f"Oficina: {oficina.nombre_oficina.upper()}      Periodo: {fecha_inicio_formateada} a {fecha_final_formateada}"
                        
    datos_adicionales = [
        [empresa],
        [nit_empresa],
        [reporte],
        [asociado],
        [detalles]                
    ]

    # Insertar los datos adicionales
    for row_num, fila in enumerate(datos_adicionales, start=1):
        for col_num, valor in enumerate(fila, start=1):
            sheet.cell(row=row_num, column=col_num, value=valor)

    # Determinar la fila donde empiezan los encabezados
    header_row = len(datos_adicionales) + 1

    # Añadir los encabezados
    headers = resultados[0].keys()
    for col_num, header in enumerate(headers, start=1):
        sheet.cell(row=header_row, column=col_num, value=header)

    # Añadir los datos
    for row_num, data in enumerate(resultados, start=header_row + 1):
        for col_num, field in enumerate(headers, start=1):
            sheet.cell(row=row_num, column=col_num, value=data[field])

    nombre_archivo = f"mov_aportes_{tercero.nombre.strip()}.xlsx"
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    workbook.save(response)
    return response
            
def exportar_csv(request, rows):
    id_cli = request.session.get('cliente_id')
    id_ofi = request.session.get('oficina_id')
    filtro_socio = request.GET.get('filtro_cod_socio', '').strip()
    fecha_ini = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_final', None)
    print('Filtro  ',filtro_socio,'    fecha_ini ',fecha_ini,'   fecha_fin ',fecha_fin)
    oficina_id = request.session.get('oficina_id')
    date_format = "%Y-%m-%d"
    fecha_actual = datetime.now()
    if fecha_ini == None:
        fecha_inicio = datetime(fecha_actual.year - 1, 1, 1).date()
    else:
        fecha_inicio = datetime.strptime(fecha_ini, date_format).date()
    if fecha_fin == None:
        fecha_final = datetime(fecha_actual.year - 1, 1, 1).date()
    else:
        fecha_final = datetime.strptime(fecha_fin, date_format).date()
    fecha_final = fecha_actual.date()
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_final_str = fecha_final.strftime('%Y-%m-%d')
    oficina_id = int(request.GET.get('oficina_id', 1))
        
    # Llama a la función para obtener los datos
    resultados = ejecutar_consulta_orm(oficina_id,filtro_socio,fecha_inicio,fecha_final)

    if len(filtro_socio) > 3: 
        resultados = ejecutar_consulta_orm(oficina_id,filtro_socio,fecha_inicio,fecha_final)
    else:
        resultados = []
    rows = []
    sal_acu = 0
    for row in resultados:
        sal_acu = sal_acu + float(row['Aporte']) - float(row['Retiro']) + float(row['Saldo'])
        upd_row = row
        upd_row['Saldo'] = sal_acu
        rows.append(upd_row)

    if not resultados:
        return HttpResponse("No se encontraron datos para exportar", status=404)
    
    tercero = TERCEROS.objects.filter(doc_ide=filtro_socio).first()         
    # Configurar la respuesta HTTP para un archivo CSV
    nombre_archivo = f"mov_aportes_{tercero.nombre.strip()}.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
                
    # Crear el escritor CSV
    writer = csv.writer(response)
                
    # Añadir encabezados de las columnas
    headers = resultados[0].keys()  # Suponemos que todos los diccionarios tienen las mismas claves
    writer.writerow(headers)

    # Añadir los datos
    for fila in resultados:
        writer.writerow([fila[col] for col in headers])
    return response
            
def imprimir(request, rows):
    id_cli = request.session.get('cliente_id')
    id_ofi = request.session.get('oficina_id')
    filtro_socio = request.GET.get('filtro_cod_socio', '').strip()
    fecha_ini = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_final', None)
    print('Filtro  ',filtro_socio,'    fecha_ini ',fecha_ini,'   fecha_fin ',fecha_fin)
    oficina_id = request.session.get('oficina_id')
    date_format = "%Y-%m-%d"
    fecha_actual = datetime.now()
    if fecha_ini == None:
        fecha_inicio = datetime(fecha_actual.year - 1, 1, 1).date()
    else:
        fecha_inicio = datetime.strptime(fecha_ini, date_format).date()
    if fecha_fin == None:
        fecha_final = datetime(fecha_actual.year - 1, 1, 1).date()
    else:
        fecha_final = datetime.strptime(fecha_fin, date_format).date()
    fecha_final = fecha_actual.date()
    
    fecha_inicio_formateada = formato_fecha(fecha_inicio)
    fecha_final_formateada = formato_fecha(fecha_final)    
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_final_str = fecha_final.strftime('%Y-%m-%d')
    oficina_id = int(request.GET.get('oficina_id', 1))

    resultados = ejecutar_consulta_orm(oficina_id,filtro_socio,fecha_inicio,fecha_final)

    if len(filtro_socio) > 3: 
        resultados = ejecutar_consulta_orm(oficina_id,filtro_socio,fecha_inicio,fecha_final)
    else:
        resultados = []
    rows = []
    sal_acu = 0
    for row in resultados:
        sal_acu = sal_acu + float(row['Aporte']) - float(row['Retiro']) + float(row['Saldo'])
        upd_row = row
        upd_row['Saldo'] = sal_acu
        rows.append(upd_row)
        
    # Lógica para imprimir o generar vista previa  Configuración del PDF
    entidad = CLIENTES.objects.filter(id=id_cli).first()
    oficina = OFICINAS.objects.filter(id=id_ofi).first()
    tercero = TERCEROS.objects.filter(doc_ide=filtro_socio).first()

    nombre_archivo = f"mov_aportes_{tercero.nombre.strip()}.pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    margin_x, margin_y = 50, 60

    # Configuración inicial
    filas_por_pagina = 64 # Número máximo de filas por página
    total_filas = len(resultados)
    total_paginas = ceil(total_filas / filas_por_pagina)

    # Función para dibujar encabezado
    def dibujar_encabezado():
        empresa = f"{entidad.nombre.strip()}"
        texto_empresa = stringWidth(empresa, "Times-Roman", 12)
        p.drawString((width - texto_empresa) / 2, height - 30, empresa)
                    
        nit_empresa = f"NIT. {entidad.doc_ide.strip()}-{entidad.dv.strip()}"
        texto_nit = stringWidth(nit_empresa, "Times-Roman", 12)
        p.drawString((width - texto_nit) / 2, height - 45, nit_empresa)

        reporte = "MOVIMIENTO DE APORTES"
        texto_reporte = stringWidth(reporte, "Times-Roman", 12)
        p.drawString((width - texto_reporte) / 2, height - 60, reporte)

        p.setFont("Helvetica", 10)
        detalles = f"Oficina: {oficina.nombre_oficina.upper()}      Periodo: {fecha_inicio_formateada} a {fecha_final_formateada}"
        texto_detalles = stringWidth(detalles, "Helvetica", 10)
        p.drawString((width - texto_detalles) / 2, height - 75, detalles)

        asociado = f"Asociado: {filtro_socio} {tercero.nombre.strip()}"
        texto_filtro = stringWidth(asociado, "Helvetica", 12)
        p.drawString((width - texto_filtro) / 2, height - 90, asociado)

        p.setFont("Helvetica", 8)
        texto_paginas = f"Pág. {pagina_actual} de {total_paginas}"
        p.drawRightString(width - margin_x, height - 90, texto_paginas)

        p.drawImage("hecho_economico_app\\Logo\\LOGO.jpg", margin_x - 20, height - margin_y - 10, 60, 60)

    # Función para dibujar pie de página
    def dibujar_pie(pagina_actual, total_paginas):
        line_y = margin_y - 30  # Ajusta para que esté justo encima del texto
        p.line(margin_x-40, line_y, margin_x+552, line_y)  # Dibuja la línea

        p.setFont("Courier", 9)
        texto_pie = f"{oficina.direccion.strip()}     Tel.: {oficina.celular.strip()}     E-mail: {oficina.email.strip()}     {oficina.ciudad.nombre.strip()}-{oficina.ciudad.departamento.strip()}"
        p.drawString(margin_x-20, margin_y - 40, texto_pie)

    # Función para dibujar encabezado de tabla
    def dibujar_encabezado_tabla(y):
        line_y = height - 115  # Ajusta para que esté justo encima del texto
        p.line(margin_x-40, line_y, margin_x+552, line_y)
        p.line(margin_x-40, height - 100, margin_x+552, height - 100)
        columnas = [
            ("Fecha", 50), 
            ("Comprobante", 180), 
            ("Número", 50), 
            ("Concepto", 60), 
            ("        Aporte", 75), 
            ("        Retiro", 75), 
            ("        Saldo", 80)
            ]
        x = margin_x-30
        p.setFont("Helvetica-Bold", 9)
        for col, ancho in columnas:
            p.drawString(x, y, col)
            x += ancho
                        
    # Dibujar contenido
    pagina_actual = 1
    dibujar_encabezado()
    dibujar_pie(pagina_actual, total_paginas)
    dibujar_encabezado_tabla(height - margin_y - 50)
    y = height - margin_y - 65

    def dibujar_fila(y, row):
        x = margin_x-30
        columnas = [
            (row['Fecha'], 50), 
            (row['Comprobante'],180), 
            (row['Numero'], 50),
            (row['Concepto'], 50), 
            (f"{row['Aporte']:,.2f}",70,'right'), 
            (f"{row['Retiro']:,.2f}", 70,'right'), 
            (f"{row['Saldo']:,.2f}", 80, 'right')
            ]

        p.setFont("Helvetica", 9)
        for col in columnas:
            if len(col) == 3 and col[2] == 'right':  # Alineación derecha
                texto, ancho, _ = col
                p.drawRightString(x + ancho, y, texto)
            else:  # Alineación izquierda
                texto, ancho = col[:2]
                p.drawString(x, y, str(texto))
            x += ancho

    for idx, row in enumerate(resultados):
        if y < margin_y - 30:
            p.showPage()
            pagina_actual += 1
            dibujar_encabezado()
            dibujar_encabezado_tabla(height - margin_y - 50)
            dibujar_pie(pagina_actual, total_paginas)
            y = height - margin_y - 65    

        dibujar_fila(y, row)
        y -= 10

    # # Resumen al final
    # p.setFont("Times-Roman", 10)
    # p.line(margin_x + 400, y - 5, margin_x + 472, y - 5)
    # p.line(margin_x + 472, y - 5, margin_x + 542, y - 5)
    # p.drawString(margin_x - 10, y - 25, "Resumen del Comprobante")
    # p.drawString(margin_x + 250, y - 25, f"Total Débitos:")
    # p.drawString(margin_x + 250, y - 40, f"Total Créditos:")
    # p.drawRightString(margin_x + 470, y - 25, f"{sum([det.debito for det in detalle_econos]):,.2f}")
    # p.line(margin_x + 400, y - 27, margin_x + 472, y - 27)
    # p.line(margin_x + 400, y - 29, margin_x + 472, y - 29)
    # p.drawRightString(margin_x + 540, y - 40, f"{sum([det.credito for det in detalle_econos]):,.2f}")
    # p.line(margin_x + 472, y - 42, margin_x + 542, y - 42)
    # p.line(margin_x + 472, y - 44, margin_x + 542, y - 44)

    p.showPage()
    p.save()
    return response
      
def liquidar_aportes(request):
    if request.method == 'POST':
        fecha_corte_str = request.POST.get('fecha_corte')
        nombre_archivo = request.POST.get('nombre_archivo')
        try:
            total_aportes = liquidar_aportes_process(fecha_corte_str, nombre_archivo, request)
            return JsonResponse({'message': 'Cálculos de liquidación iniciados.'})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return render(request, 'aportes_a_la_fecha.html')

    print('Total aportes--->', total_aportes)

def liquidar_aportes_process(fecha_corte_str, nombre_archivo, request):
    # Lógica para exportar Crear el libro de Excel
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Saldo Aportes" 

    fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
    if not os.path.exists(os.path.dirname(nombre_archivo)):
        raise ValueError("El directorio especificado no existe.")
    
    resultados = []
    print('Hora de Inicio ',datetime.now())
    result= (
        DETALLE_PROD.objects.filter(
            producto = 'AP',
            hecho_econo__fecha__lte = fecha_corte,
            hecho_econo__docto_conta__oficina_id=1
        )
        .values('subcuenta')  # Agrupamos por 'subcuenta'
        .annotate(
            cod_aso=F('subcuenta'),
            Aporte_fecha=-Sum(F('valor')),  # Negamos la suma como en la SQL
            fec_ult_apo=Max('hecho_econo__fecha')
        )
    )
    result_list = list(result)
    for item in result_list:
        if item['Aporte_fecha'] is not None or item['fec_ult_apo'] is not None:
            asociado = ASOCIADOS.objects.filter(oficina_id = 1,cod_aso = item['cod_aso']).first()
            if asociado == None:
                print('No Hay Asociado con código ',item['cod_aso'])
                continue
            if asociado.tercero_id == None:
                print('Error de Integridad cod_aso ',asociado.cod_aso)
                continue
            tercero = TERCEROS.objects.filter(id = asociado.tercero_id).first()
            if tercero != None:
                resultados.append({
                    'cod_aso': asociado.cod_aso,
                    'nombre': tercero.nombre,
                    'Aporte_fecha': item['Aporte_fecha'],
                    'fec_ult_apo': item['fec_ult_apo']
                })

    print('Hora de Final  ',datetime.now())  
    nombre_archivo = f"saldo_aportes.xlsx"
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    workbook.save(response)  

    # df = pd.DataFrame(resultados)
    # df.to_excel(nombre_archivo, index=False)

def saldo_aportes_fecha(oficina_id, subcuenta, fecha_corte):

    result = (
        DETALLE_PROD.objects.filter(
            producto='AP',
            subcuenta=subcuenta,
            hecho_econo__fecha__lte=fecha_corte,
            hecho_econo__docto_conta__oficina_id=oficina_id
        )
        .exclude(concepto='APREV')
        .annotate(
            cod_aso=F('subcuenta'),
            Aporte_fecha=-Sum(F('valor')),  # Negamos la suma como en la SQL
            fec_ult_apo=Max('hecho_econo__fecha')
        )
        .order_by('-hecho_econo__fecha')  # Ordenar por fecha descendente
        .values('cod_aso', 'Aporte_fecha', 'hecho_econo__fecha')
        .first()  # Retorna un único registro o None si no hay resultados
    )
    return result

def saldo_aporte_socio_fecha(oficina_id, subcuenta, fecha_corte):
    saldo = (
        DETALLE_PROD.objects
            .filter(
                oficina_id = oficina_id,
                producto = "AP",
                subcuenta = subcuenta,
                hecho_econo__fecha__lt = fecha_corte
            )
        .aggregate(saldo=Coalesce(Sum("valor"), Value(0, output_field=FloatField())))
    ) 
    return -saldo["saldo"]

def saldo_aportes(request):
    id_cli = request.session.get('cliente_id')
    id_ofi = request.session.get('oficina_id')
    if request.method == 'GET':
        return render(request, 'saldo_aportes.html') 
    if request.method == 'POST':
        id_cli = request.session.get('cliente_id')
        id_ofi = request.session.get('oficina_id')
        accion = request.POST.get("accion")   
      
        fecha_corte = request.POST.get('fecha_corte1')
            
        saldos = obtener_reporte(id_cli, id_ofi, fecha_corte)

        if accion == "exportar":
            id_cli = request.session.get('cliente_id')
            id_ofi = request.session.get('oficina_id')
        
            # Lógica para exportar Crear el libro de Excel
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "SALDO APORTES A UNA FECHA" 

            entidad = CLIENTES.objects.filter(id=id_cli).first()
            oficina = OFICINAS.objects.filter(id=id_ofi).first()

            # Llama a la función para obtener los datos        
            saldos = obtener_reporte(id_cli, id_ofi, fecha_corte)                            
            if not saldos:
                return HttpResponse("No se encontraron datos para exportar", status=404)
                      
            fecha_corte_formateada = formato_fecha(fecha_corte)
            
            # Añadir datos adicionales encima de los encabezados
            empresa = f"{entidad.nombre.strip()}"
            nit_empresa = f"NIT. {entidad.doc_ide.strip()}-{entidad.dv.strip()}"
            reporte = f"SALDO DE APORTES A LA FECHA {fecha_corte_formateada}"
            detalles = f"Oficina: {oficina.nombre_oficina.upper()}"
                                
            datos_adicionales = [
                [empresa],
                [nit_empresa],
                [reporte],
                [detalles]                
            ]

            # Insertar los datos adicionales
            for row_num, fila in enumerate(datos_adicionales, start=1):
                for col_num, valor in enumerate(fila, start=1):
                    sheet.cell(row=row_num, column=col_num, value=valor)

            # Determinar la fila donde empiezan los encabezados
            header_row = len(datos_adicionales) + 1

            # Añadir los encabezados
            headers = saldos[0].keys()
            for col_num, header in enumerate(headers, start=1):
                sheet.cell(row=header_row, column=col_num, value=header)

            # Añadir los datos
            for row_num, data in enumerate(saldos, start=header_row + 1):
                for col_num, field in enumerate(headers, start=1):
                    sheet.cell(row=row_num, column=col_num, value=data[field])

            nombre_archivo = f"saldo_aportes_{fecha_corte_formateada}.xlsx"
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            workbook.save(response)
            return response
           
        elif accion == "csv":
            id_cli = request.session.get('cliente_id')
            id_ofi = request.session.get('oficina_id')
                            
            # Llama a la función para obtener los datos
            saldos = obtener_reporte(id_cli, id_ofi, fecha_corte)
           
            if not saldos:
                return HttpResponse("No se encontraron datos para exportar", status=404)
            
            # Configurar la respuesta HTTP para un archivo CSV
            nombre_archivo = f"saldo_aportes_{fecha_corte_formateada}.csv"
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
                        
            # Crear el escritor CSV
            writer = csv.writer(response)
                        
            # Añadir encabezados de las columnas
            headers = saldos[0].keys()  # Suponemos que todos los diccionarios tienen las mismas claves
            writer.writerow(headers)

            # Añadir los datos
            for fila in saldos:
                writer.writerow([fila[col] for col in headers])
            return response
        else:
            return HttpResponse("Acción no permitida", status=405)
                
    return render(request, 'saldo_aportes.html') 
#     return HttpResponse("Método no permitido", status=405)

def score_creditos_por_nit(oficina_id, fecha_corte):
    fecha_limite = fecha_corte - timedelta(days=365*3)
    resultado = (
        CARTE_CAT_HIS.objects
        .filter(oficina_id=oficina_id, fecha__gt=fecha_corte - timedelta(days=365*3))  # Filtro de fecha
        .values("nit")  # Agrupar por `nit`
        .annotate(
            suma_cat_arr=Coalesce(
                Sum(
                    Case(
                        When(cat_arr="A", then=Value(1.0)),  # Si ARRASTRE es "A", contar 1.0
                        default=Value(0.0),  # De lo contrario, 0.0
                        output_field=FloatField(),
                    )
                ),
                Value(0.0)  # Si no hay valores, poner 0.0
            ),
            conteo_total=Coalesce(Count("id", output_field=FloatField()), Value(1.0)),  # Contar total, evitar división por 0
        )
        .annotate(porcentaje=F("suma_cat_arr") / F("conteo_total") * 100)  # Calcular el porcentaje
    )
    #print("🔍 Resultado QuerySet:", list(resultado))
    return {item["nit"]: item["porcentaje"] for item in resultado}

def contar_creditos_socio(oficina_id, fecha_limite):
    # Ejecutar una sola consulta y devolver un diccionario {cod_aso: total}
    resultado = (
        CREDITOS.objects
        .filter(
            oficina_id=oficina_id,
            fec_des__lt=fecha_limite
        )
        .exclude(estado="X")
        .values("socio__cod_aso")  # Agrupar por socio
        .annotate(total=Count("id"))  # Contar los créditos por socio
    )

    # Convertir resultados en un diccionario {cod_aso: total}
    return {item["socio__cod_aso"]: item["total"] for item in resultado}

def obtener_reporte(cliente_id, oficina_id, fecha_corte_str):
   
    NIV_EST_DICT = dict(OPC_EDUCACION)
    EST_CIV_DICT = dict(OPC_EST_CIV)
    EST_SOC_DICT = dict(OPC_EST_SOCIO)

    fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
    print('Fecha Corte',fecha_corte,'  ',type(fecha_corte))
    print('Inicio aportes apoRtes    ',datetime.now())
    creditos_socio = contar_creditos_socio(oficina_id, fecha_corte)
    score_nit = score_creditos_por_nit(oficina_id, fecha_corte)

    asociados = list(ASOCIADOS.objects.filter(
         oficina_id=oficina_id
        ).exclude(
            estado='R', 
            fec_ret__lt=fecha_corte
        ).annotate(
            fecha_maxima=Max('tercero__estados_fin__fec_inf')  # Fecha más reciente por tercero
            ).filter(
            tercero__estados_fin__fec_inf=F('fecha_maxima')
        ).values(
            'tercero__cla_doc', 'cod_aso', 'tercero__nombre', 'fec_afi', 'tercero__cod_ciu_res_id__codigo', 
            'tercero__direccion', 'tercero__celular1', 'estado', 'sexo', 'emp_ent', 'fec_nac', 'tercero__doc_ide', 
            'tercero__email', 'niv_est', 'ocupacion', 'tercero__estados_fin__ing_tot', 'estrato', 'zona', 'cab_fam', 'est_civ', 'per_a_cargo', 'num_hij_may',
            'num_hij_men', 'tip_viv'
    ))

    for asociado in asociados:
        asociado['total_aportes'] = saldo_aporte_socio_fecha(oficina_id,asociado['cod_aso'],fecha_corte)
        asociado['apo_esperado'] = aporte_esperado_fecha(asociado['cod_aso'],fecha_corte)
        asociado['total_creditos'] = creditos_socio.get(asociado['tercero__doc_ide'], 0)
        asociado['score_cartera'] = score_nit.get(asociado['tercero__doc_ide'],0)
        asociado['niv_est'] = NIV_EST_DICT.get(asociado['niv_est'], "Sin Estudio").upper()
        asociado['est_civ'] = EST_CIV_DICT.get(asociado['est_civ'], "Sin Estado Civil").upper()
        asociado['estado'] = EST_SOC_DICT.get(asociado['estado'], "Asociado Sin Estado").upper()
        if asociado['fec_nac']:
            asociado['edad'] = calcular_edad(asociado['fec_nac'], fecha_corte)
        else:
            asociado['edad'] = None  # O un valor predeterminado
        if asociado['fec_afi']:
            asociado['ant_mes'] = calcular_antiguedad(asociado['fec_afi'], fecha_corte)
        else:
            asociado['ant_mes'] = None  # O un valor predeterminado      
       
    orden = [
        'tercero__cla_doc', 'cod_aso', 'tercero__nombre', 'fec_afi', 'tercero__cod_ciu_res_id__codigo',
        'tercero__direccion', 'tercero__celular1', 'total_aportes', 'estado', 'sexo', 
        'emp_ent', 'fec_nac', 'tercero__doc_ide', 'tercero__email', 'edad', 'score_cartera', 
        'ant_mes', 'total_creditos', 'niv_est', 'ocupacion', 'tercero__estados_fin__ing_tot', 'estrato', 'zona', 
        'cab_fam', 'per_a_cargo', 'num_hij_may', 'num_hij_men', 'tip_viv', 'apo_esperado'
        ]
    
    renombrar = {
        'tercero__cla_doc': 'Tip_Doc',
        'cod_aso': 'Cod_Aso',
        'tercero__nombre': 'Nombre Completo',
        'fec_afi': 'Fec_Afi',
        'tercero__cod_ciu_res_id__codigo': 'Ciudad',
        'tercero__direccion': 'Dirección',
        'tercero__celular1': 'Teléfono',
        'total_aportes': 'Total Aportes',
        'estado': 'Estado',
        'sexo': 'Sexo',
        'emp_ent': 'Empleado_Ent',
        'fec_nac': 'Fec_Nac',
        'tercero__doc_ide': 'NIT',
        'tercero__email': 'Email',
        'edad': 'Edad',
        'score_cartera': 'Score_Car',
        'ant_mes': 'Ant_(Meses)',
        'total_creditos': 'Num_Cre',
        'niv_est': 'Niv_Est',
        'ocupacion': 'Ocupacion',
        'tercero__estados_fin__ing_tot': 'Niv_Ingreso',
        'estrato': 'Estrato',
        'zona': 'Zona',
        'cab_fam': 'Cab_Fam',
        'per_a_cargo': 'Per_a_Cargo',
        'num_hij_may': 'Num_Hij_May',
        'num_hij_men': 'Num_Hij_Men',
        'tip_viv': 'Tip_Viv',
        'apo_esperado': 'Apor_al_dia'
        }
    # Reorganizar los diccionarios en el orden deseado
    for asociado in asociados:
        asociado_ordenado = {campo: asociado.get(campo) for campo in orden}
        asociado.clear()
        asociado.update({renombrar.get(k, k): v for k, v in asociado_ordenado.items()})
    
    return asociados

# Funciones auxiliares
def calcular_antiguedad(fecha_afiliacion, fecha_corte):
    ant_mes = (fecha_corte.year - fecha_afiliacion.year)* 12 + (
        (fecha_corte.month)-(fecha_afiliacion.month)
        )
    return ant_mes

def calcular_edad(fecha_nacimiento, fecha_corte):
    edad = fecha_corte.year - fecha_nacimiento.year - (
        (fecha_corte.month, fecha_corte.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )
    return edad

def aporte_esperado_fecha(cod_aso, fec_cor):
    asociado = ASOCIADOS.objects.filter(cod_aso=cod_aso,oficina = 1).first()
    x_tip_soc = asociado.tercero.tip_ter
    xAgnoIni = asociado.fec_afi.year
    plan_apo = PLAN_APORTES.objects.filter(agno = xAgnoIni).first()
    if x_tip_soc == "J":
        x_tot_apo_esp = plan_apo.inijur
        x_dia_ing = 0
    else:
        x_dia_ing = (asociado.fec_afi - asociado.fec_nac).days
        if x_dia_ing < 365 * 18:
            x_tot_apo_esp = plan_apo.inichi2
        else:
            x_tot_apo_esp = plan_apo.iniadu
    aportaciones = PLAN_APORTES.objects.all()
    for aportacion in aportaciones:
        if aportacion.agno <= fec_cor.year:
            if x_tip_soc == "J":
                x_tot_apo_esp += (
                    (aportacion.totadu / 12 * (12 - asociado.fec_afi.month))
                    if aportacion.agno == asociado.fec_afi.year else aportacion.totadu
                ) - (
                    (aportacion.totadu / 12 * (12 -fec_cor.month))
                    if aportacion.agno == fec_cor.year else 0
                )
            else:
                if x_dia_ing < 365 * 18:
                    x_tot_apo_esp += (
                        (aportacion.totchi2 / 12 * (12 - asociado.fec_afi.month))
                        if aportacion.agno == asociado.fec_afi.year else aportacion.totchi2
                    ) - (
                        (aportacion.totchi2 / 12 * (12 - asociado.fec_afi.month)) * aportacion.meses / 12
                        if aportacion.agno == fec_cor.year else 0
                    )
                else:
                    x_tot_apo_esp += (
                        (aportacion.totadu / 12 * (12 - fec_cor.month))
                        # (aportacion.totadu / 12 * (12 -asociado.fec_afi.month))
                        if aportacion.agno == fec_cor.year else aportacion.totadu
                        # if aportacion.agno == asociado.fec_afi.year else aportacion.totadu
                    ) - (
                        (aportacion.totadu / 12 * (12 - fec_cor.month)) * aportacion.meses / 12
                        # (aportacion.totadu / 12 * (12 - asociado.fec_afi.month)) * aportacion.meses / 12
                        if aportacion.agno == fec_cor.year else 0
                    )
        x_dia_ing += 365
    return x_tot_apo_esp

def aporte_mensual(oficina_id, cod_aso, fec_cor):
    asociado = ASOCIADOS.objects.filter(cod_aso=cod_aso, oficina=oficina_id).first()
    if not asociado:
        return 0  # Si no existe el asociado, retornar 0
    
    x_tip_soc = asociado.tercero.tip_ter
    plan_apo = PLAN_APORTES.objects.filter(agno=fec_cor.year).first()

    if not plan_apo:
        return 0  # Si no hay plan de aportes para ese año, retornar 0

    # Determinar el aporte anual según el tipo de asociado
    if x_tip_soc == "J":
        aporte_anual = plan_apo.totjur  # Persona jurídica usa totjur
    else:
        x_dia_ing = (fec_cor - asociado.fec_nac).days
        if x_dia_ing < 365 * 18:
            aporte_anual = plan_apo.totchi2  # Chico 1 y 2
        else:
            aporte_anual = plan_apo.totadu  # Adulto

    # Calcular el aporte mensual dividiendo el anual entre 12
    aporte_mensual = aporte_anual / 12

    return round(aporte_mensual, 2)  # Redondear a 2 decimales

def aportes_super(request):
    id_cli = request.session.get('cliente_id')
    id_ofi = request.session.get('oficina_id')
    if request.method == 'GET':
        return render(request, 'aportes_supersolidaria.html') 
    if request.method == 'POST':
        id_cli = request.session.get('cliente_id')
        id_ofi = request.session.get('oficina_id')
        accion = request.POST.get("accion")   
      
        fecha_corte = request.POST.get('fecha_corte')
            
        saldos = reporte_super(id_cli, id_ofi, fecha_corte)

        if accion == "exportar":
            id_cli = request.session.get('cliente_id')
            id_ofi = request.session.get('oficina_id')
        
            # Lógica para exportar Crear el libro de Excel
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "APORTES SUPERSOLIDARIA" 

            entidad = CLIENTES.objects.filter(id=id_cli).first()
            oficina = OFICINAS.objects.filter(id=id_ofi).first()

            # Llama a la función para obtener los datos        
            saldos = reporte_super(id_cli, id_ofi, fecha_corte)                            
            if not saldos:
                return HttpResponse("No se encontraron datos para exportar", status=404)
                      
            fecha_corte_formateada = formato_fecha(fecha_corte)
                        
            # Añadir datos adicionales encima de los encabezados
            empresa = f"{entidad.nombre.strip()}"
            nit_empresa = f"NIT. {entidad.doc_ide.strip()}-{entidad.dv.strip()}"
            reporte = f"APORTES SUPERSOLIDARIA A LA FECHA {fecha_corte_formateada}"
            detalles = f"Oficina: {oficina.nombre_oficina.upper()}"
                                
            datos_adicionales = [
                [empresa],
                [nit_empresa],
                [reporte],
                [detalles]                
            ]

            # Insertar los datos adicionales
            for row_num, fila in enumerate(datos_adicionales, start=1):
                for col_num, valor in enumerate(fila, start=1):
                    sheet.cell(row=row_num, column=col_num, value=valor)

            # Determinar la fila donde empiezan los encabezados
            header_row = len(datos_adicionales) + 1

            # Añadir los encabezados
            headers = saldos[0].keys()
            for col_num, header in enumerate(headers, start=1):
                sheet.cell(row=header_row, column=col_num, value=header)

            # Añadir los datos
            for row_num, data in enumerate(saldos, start=header_row + 1):
                for col_num, field in enumerate(headers, start=1):
                    sheet.cell(row=row_num, column=col_num, value=data[field])

            nombre_archivo = f"aportes_supersolidaria_{fecha_corte_formateada}.xlsx"
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            workbook.save(response)
            return response
           
        elif accion == "csv":
            id_cli = request.session.get('cliente_id')
            id_ofi = request.session.get('oficina_id')
                            
            # Llama a la función para obtener los datos
            saldos = reporte_super(id_cli, id_ofi, fecha_corte)
           
            if not saldos:
                return HttpResponse("No se encontraron datos para exportar", status=404)
            
            # Configurar la respuesta HTTP para un archivo CSV
            nombre_archivo = f"aportes_supersolidaria_{fecha_corte}.csv"
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
                        
            # Crear el escritor CSV
            writer = csv.writer(response)
                        
            # Añadir encabezados de las columnas
            headers = saldos[0].keys()  # Suponemos que todos los diccionarios tienen las mismas claves
            writer.writerow(headers)

            # Añadir los datos
            for fila in saldos:
                writer.writerow([fila[col] for col in headers])
            return response
        else:
            return HttpResponse("Acción no permitida", status=405)
                
    return render(request, 'aportes_supersolidaria.html')

def reporte_super(cliente_id, oficina_id, fecha_corte_str):

    fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
    
    asociados = obtener_reporte(cliente_id, oficina_id, fecha_corte_str)
    
    for asociado in asociados:
        fecha_aporte = saldo_aportes_fecha(oficina_id,  asociado['Cod_Aso'], fecha_corte)
        asociado['tip_doc'] = asociado['Tip_Doc']
        asociado['cod_aso'] = asociado['Cod_Aso']
        asociado['total_aportes'] = asociado['Total Aportes']
        asociado['aporte_mensual'] = aporte_mensual(oficina_id, asociado['Cod_Aso'], fecha_corte)
        asociado['aporte_ordinario'] =asociado['Total Aportes']
        asociado['aporte_extra_ordinario'] = 0
        asociado['revalorizacion'] = 0
        asociado['aporte_voluntario'] = 0
        asociado['aporte_esperado'] = asociado['Apor_al_dia']
        # asociado['aporte_esperado'] = asociado.get('Apor_al_dia')
        # ult_apo = saldo_aportes_fecha(oficina_id, asociado['cod_aso'], fecha_corte)
        asociado['fec_ult_apo'] = fecha_aporte["hecho_econo__fecha"] if fecha_aporte else None
                                   
    orden = [
        'tip_doc', 'cod_aso', 'total_aportes', 'aporte_mensual', 'aporte_ordinario','aporte_extra_ordinario', 'revalorizacion', 'aporte_voluntario', 'aporte_esperado', 'fec_ult_apo'
        ]
    
    renombrar = {
        'tip_doc': 'Tip_Doc',
        'cod_aso': 'Cod_Aso',
        'total_aportes': 'Total Aportes',
        'aporte_mensual': 'Aporte Mensual',
        'aporte_ordinario': 'Aporte Ordinario',
        'aporte_extra_ordinario': 'Aporte Extra',
        'revalorizacion': 'Revalorizacion',
        'aporte_voluntario': 'Aporte Voluntario',
        'aporte_esperado': 'Aporte Esperado',
        'fec_ult_apo': 'Fec_Ult_Apo'
        }
    
    # asociados_filtrados = asociados.filter(total_aportes__gt=0)
    asociados_filtrados = [a for a in asociados if a.get('total_aportes', 0) > 0]
    # Reorganizar los diccionarios en el orden deseado
    for asociado in asociados:
        asociado_ordenado = {campo: asociado.get(campo) for campo in orden}
        asociado.clear()
        asociado.update({renombrar.get(k, k): v for k, v in asociado_ordenado.items()})
    
    asociados_ordenados = sorted(asociados_filtrados, key=lambda x: x.get('Cod_Aso', ''))
    
    return asociados_ordenados
    