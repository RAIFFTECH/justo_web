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
from .models import ACTIVOS_FIJOS
from clientes_app.models import CLIENTES
from oficinas_app.models import OFICINAS
from asociados_app.models import ASOCIADOS
from terceros_app.models import TERCEROS
from detalle_producto_app.models import DETALLE_PROD
from detalle_economico_app.models import DETALLE_ECONO
from hecho_economico_app.models import HECHO_ECONO
from documentos_app.models import DOCTO_CONTA
from cuentas_app.models import PLAN_CTAS
from creditos_app.models import CREDITOS
from estados_financieros_app.models import ESTADOS_FIN
from localidades_app.models import LOCALIDADES
from recla_carte_app.models import CARTE_CAT_HIS
from justo_app.opciones import OPC_EST_SOCIO, OPC_EDUCACION, OPC_EST_CIV
from justo_app.funciones_principales import formato_fecha

# Para obtener todos los registros
class Lista(LoginRequiredMixin, ListView):
    model = ACTIVOS_FIJOS
    form = CrearForm
    template_name = 'lista_activos_fijos.html'
    # ordering = ['cliente','per_con','cod_cta']

# Para obtener todos los detalles de un registro
class Detalles(LoginRequiredMixin, DetailView):
    model = ACTIVOS_FIJOS
    form = CrearForm
    template_name = 'detalles_activos_fijos.html'

# Para crear un nuevo registro
class Crear(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ACTIVOS_FIJOS
    form = CrearForm
    fields = '__all__'
    template_name = 'crear_activos_fijos.html'

    # Mensaje que se mostrará cuando se inserte el registro
    success_message = 'Registro añadido correctamente.'

    # Redirigimos a la página principal tras insertar el registro
    def get_success_url(self):
        return reverse('listar_activos_fijos')

# Para modificar un registro
class Actualizar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ACTIVOS_FIJOS
    form = CrearForm
    fields = '__all__'
    template_name = 'actualizar_activos_fijos.html'
    # Mensaje que se mostrará cuando se actualice el registro
    success_message = 'Registro actualizado correctamente.'

    # Redireccionamos a la página principal tras actualizar el registro
    def get_success_url(self):
        return reverse('listar_activos_fijos')

# Para eliminar un registro
class Eliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ACTIVOS_FIJOS
    form = CrearForm
    fields = "__all__"

    # Redireccionamos a la página principal tras de eliminar el registro
    def get_success_url(self):
        # Mensaje que se mostrará cuando se elimine el registro
        success_message = 'Registro eliminado correctamente.'
        messages.success(self.request, (success_message))
        return reverse('listar_activos_fijos')
    

# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import ComprobanteDepreciacionForm
from datetime import datetime
from django.contrib.sessions.models import Session

# Vista para mostrar el formulario
from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime, timedelta
from .forms import ComprobanteDepreciacionForm

from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from .forms import ComprobanteDepreciacionForm  # Importa tu formulario

def generar_comprobante_view(request):
    # Obtener el año desde la sesión
    oficina_id = request.session.get('oficina_id', None)
    per_con = request.session.get('per_con', None)
    if not per_con:
        return redirect('error')  # Si no hay año en la sesión, redirigir a error
    form = ComprobanteDepreciacionForm(request.POST or None)
    pk = None  # Inicialmente no hay pk
    mensaje = None  # Inicialmente no hay mensaje
    mes = None  # Inicializamos el mes como None

    if request.method == 'POST' and form.is_valid():
        # Obtener el mes seleccionado
        mes = form.cleaned_data['mes']
        mensaje = ''
        CompAnt = HECHO_ECONO.objects.filter(
            docto_conta__oficina_id=oficina_id,
            docto_conta__per_con=per_con,
            docto_conta__codigo=11
        ).order_by('-fecha').first()
        
        Comp =  HECHO_ECONO.objects.filter(docto_conta__oficina_id = oficina_id,
            docto_conta__per_con = per_con,docto_conta__codigo = 11,numero = mes).first()
        if Comp != None:
            print('Existe el comprobante')
            mensaje = 'El Comprobante Existe'
            if Comp.protegido == 'S' :
                meensaje = 'El Comprobante Existe y esta protegido '
        
        pk = hacer_comprobante(oficina_id,per_con,int(mes))

    return render(request, 'generar_comprob_form.html', {
        'form': form,
        'año': per_con,
        'pk': pk,  # Pasamos el pk (o None si no se ha generado)
        'mensaje': mensaje,
        'mes': mes  # Pasamos el mes seleccionado a la plantilla
    })

def hacer_comprobante(oficina_id,per_con,mes):
    ofi = OFICINAS.objects.filter(id = oficina_id).first()
    cli = CLIENTES.objects.filter(id = ofi.cliente_id).first()
    ter = TERCEROS.objects.filter(cliente_id = cli.id,doc_ide = '892000914').first()
    primer_dia_mes_siguiente = datetime(per_con, mes % 12 + 1, 1)
    fecha_comp = primer_dia_mes_siguiente - timedelta(days=1)
    fecha_comp = fecha_comp.date()
    docto = DOCTO_CONTA.objects.filter(oficina_id = oficina_id,per_con = per_con,codigo = 11).first()
    comprob = HECHO_ECONO.objects.filter(docto_conta = docto,numero = mes,fecha = fecha_comp).first()
    if comprob != None:
        DETALLE_PROD.objects.filter(hecho_econo = comprob).delete()
    else:
       comprob = HECHO_ECONO.objects.create(docto_conta = docto,numero = mes,fecha = fecha_comp)
    comprob.descripcion = 'asiento de depreciasion del meS'
    ACT_FIJ = ACTIVOS_FIJOS.objects.filter(oficina_id = oficina_id)
    for regact in ACT_FIJ:
        xfec_alt = regact.fecha_de_alta
        if (regact.meses_dep > 0 and xfec_alt < fecha_comp) and regact.de_baja != 'S':
            resultado = DETALLE_ECONO.objects.filter(
                referencia = regact.codigo,hecho_econo__fecha__lte = fecha_comp,
                hecho_econo__docto_conta__oficina_id = 1,hecho_econo__docto_conta__codigo = 11
            ).aggregate(total_credito=Sum('credito'))
            dep_acu = resultado['total_credito'] or 0
            if xfec_alt.year == fecha_comp.year and xfec_alt.month == fecha_comp.month:
                dias_dep =  (fecha_comp - xfec_alt).days
            else:
                dias_dep = 30
            if dep_acu > 0 :
                dep_mes = 0                    
                if regact.valor_elem - regact.valor_salva - regact.dep_acu_vig_ant > 0:         
                    if (round((regact.valor_elem - regact.valor_salva) / regact.meses_dep,0) <= regact.valor_elem  - regact.valor_salva - regact.val_acu_vig_ant - dep_acu):
                        dep_mes = round((regact.valor_elem - regact.valor_salva) / regact.meses_dep * dias_dep/30,0)
                    else:
                        dep_mes = regact.valor_elem - regact.valor_salva - regact.val_acu_vig_ant - dep_acu
                        dias_dep = int(dep_mes / ((regact.valor_elem - regact.valor_salva) / dias_dep)*30)
                        dias_dep = 30 if dias_dep > 30 else dias_dep
                    if regact.meses_dep == 1:
                        dep_mes = regact.valor_elem  - regact.valor_salva - regact.val_acu_vig_ant - dep_acu
                    id_cta_dep = PLAN_CTAS.objects.filter(cliente = cli,per_con = per_con,cod_cta = regact.cod_cta_dep).first()
                    id_cta_dep_gas = PLAN_CTAS.objects.filter(cliente = cli,per_con = per_con,cod_cta = regact.cod_cta_dep_gas).first()
                    det_ecod = DETALLE_ECONO.objects.create(hecho_econo = comprob,item_concepto = 'DepMes',detalle = 'dEpmes '+regact.codigo,
                        cuenta_id = id_cta_dep.id,tercero = ter,debito = 0,credito = dep_mes,referencia = regact.codigo)
                    det_ecod.save()
                    det_ecoc = DETALLE_ECONO.objects.create(hecho_econo = comprob,item_concepto = 'DepMes',detalle = 'dEpmes '+regact.codigo,
                        cuenta_id = id_cta_dep_gas.id,tercero = ter,debito = dep_mes,credito = 0,referencia = regact.codigo)
                    det_ecoc.save()
    return comprob.id
    


# Vista para ver el comprobante (Aquí solo ejemplo)
# views.py
def ver_comprobante_view(request, pk):
    # Lógica para mostrar el comprobante de depreciación basado en el pk
    #comprobante = ComprobanteDepreciacion.objects.get(pk=pk)

    return render(request, 'ver_comprobante.html', {'comprobante': comprobante})

def exportar_excel(request, pk):
    # Lógica para exportar el comprobante a Excel
    #comprobante = ComprobanteDepreciacion.objects.get(pk=pk)
    # Aquí deberías usar alguna librería para generar Excel, como openpyxl o pandas
    # Devuelve un archivo de Excel
    return HttpResponse('Excel Exported')

def exportar_csv(request, pk):
    # Lógica para exportar el comprobante a CSV
    #comprobante = ComprobanteDepreciacion.objects.get(pk=pk)
    # Genera un CSV
    return HttpResponse('CSV Exported')

