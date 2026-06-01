from .models import(HECHO_ECONO)
from detalle_economico_app.models import DETALLE_ECONO
from detalle_producto_app.models import DETALLE_PROD
from .serializers import (HechoEconoListadoSerializer)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, mixins, generics, viewsets
from rest_framework.fields import BooleanField, DateField
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework import exceptions
from .serializers import HechoEconoListadoSerializer,DetalleEconoSerializer,DetalleProdSerializer
from documentos_app.models import DOCTO_CONTA
from justo_app.opciones import OPC_CANALES
from hecho_economico_app.models import HECHO_ECONO
from cuentas_app.models import PLAN_CTAS
from localidades_app.models import LOCALIDADES
from django.http import JsonResponse
from terceros_app.models import TERCEROS
from asociados_app.models import ASOCIADOS
from creditos_app.models import CREDITOS
from conceptos_app.models import CONCEPTOS
from ctas_ahorros_app.models import CTAS_AHORRO
from cxc_app.models import CTAS_X_COBRAR,CXC_DET
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import datetime
from django.utils.html import escape
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms_old import HechoEconoForm,DetalleProdForm
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def buscar_hechos_econo(request):
    filtro_texto = request.GET.get('filtro_texto', '')
    hechos_econo = HECHO_ECONO.objects.filter(descripcion__icontains=filtro_texto) | \
                   HECHO_ECONO.objects.filter(numero__icontains=filtro_texto)
    paginator = Paginator(hechos_econo, 10)  # muestra 10 registros por página
    page = request.GET.get('page')

    try:
        hechos_econo_pagina = paginator.page(page)
    except PageNotAnInteger:
        hechos_econo_pagina = paginator.page(1)
    except EmptyPage:
        hechos_econo_pagina = paginator.page(paginator.num_pages)

    return render(request, 'template.html', {'hechos_econo': hechos_econo_pagina, 'filtro_texto': filtro_texto})


def hecho_detalles_lista(request, hecho_id):
    hecho = get_object_or_404(HECHO_ECONO, pk=hecho_id)
    hecho_items = DETALLE_PROD.objects.filter(hecho_econo=hecho)
    hecho_data = {
        'id': hecho.id,
        'numero': hecho.numero,
        'fecha': hecho.fecha.strftime('%Y-%m-%d'),
        'canal': hecho.canal,
        'descripcion': hecho.descripcion,
        'docto_conta_id': hecho.docto_conta_id,
        'protegido': hecho.protegido,
        'anulado': hecho.anulado,
        'items': []
    }
    for item in hecho_items:
        item_data = {
            'id': item.id,
            'producto': item.producto,
            'concepto': item.concepto,
            'subcuenta': item.subcuenta,
            'valor': item.valor,
        }
        if item.producto == 'AP':
            asociado = ASOCIADOS.objects.filter(oficina_id = 1,cod_aso = item.subcuenta).first() 
            tercero = TERCEROS.objects.filter(cliente_id = 1,id = asociado.tercero_id).first()
            item_data['tercero'] = tercero.nombre
        elif item.producto == 'AH':
            cta_ahorro = CTAS_AHORRO.objects.filter(oficina_id = 1,num_cta = item.subcuenta).first() 
            asociado = ASOCIADOS.objects.filter(oficina_id = 1,id = cta_ahorro.asociado_id).first() 
            tercero = TERCEROS.objects.filter(cliente_id = 1,id = asociado.tercero_id).first()
            item_data['tercero'] = tercero.nombre
        elif item.producto == 'CR':
            credito = CREDITOS.objects.filter(oficina_id = 1,cod_cre = item.subcuenta).first() 
            if credito == None:
                item_data['tercero'] = 'Indefinido'
                continue
            asociado = ASOCIADOS.objects.filter(oficina_id = 1,id = credito.socio_id).first() 
            tercero = TERCEROS.objects.filter(cliente_id = 1,id = asociado.tercero_id).first()
            item_data['tercero'] = tercero.nombre
        else:
            item_data['tercero'] = 'Indefinido'
        hecho_data['items'].append(item_data)

    context = {
        'data_json': escape(json.dumps(hecho_data))
    }
    
    return render(request, 'hecho_econo.html',context)

from django.db.models import Sum, Value, F
    
def buscar_subcuenta(request):
    cod_con = request.GET.get('cod_con')
    filtro = request.GET.get('filtro')
    concepto = CONCEPTOS.objects.filter(cliente_id = 1,cod_con = cod_con).first()
    results = []
    if concepto == None:
        return JsonResponse(results, safe=False)
    terceros = TERCEROS.objects.filter(Q(cliente_id = 1) & (Q(nombre__icontains=filtro) | Q(doc_ide__icontains=filtro)))[:100]  
    if concepto.tip_sis == '1':    
        for tercero in terceros: 
            asociado = ASOCIADOS.objects.filter(oficina_id = 1,cod_aso=tercero.doc_ide).first()
            if asociado != None:
                results.append({'subcuenta': asociado.cod_aso , 'nombre': tercero.nombre.rstrip()})
    elif concepto.tip_sis == '2':
        for tercero in terceros: 
            asociado = ASOCIADOS.objects.filter(oficina_id = 1,cod_aso=tercero.doc_ide).first()
            if asociado != None:
                cta_ahorro = CTAS_AHORRO.objects.filter(oficina_id = 1,asociado_id = asociado.id)
                for cuenta in cta_ahorro:
                    results.append({'subcuenta': cuenta.num_cta, 'nombre': tercero.nombre.rstrip()})
    elif concepto.tip_sis == '3':
        for tercero in terceros: 
            asociado = ASOCIADOS.objects.filter(oficina_id = 1,cod_aso=tercero.doc_ide).first()
            if asociado != None:
                if cod_con == 'DESEM':
                    creditos = CREDITOS.objects.filter(oficina_id = 1,socio_id = asociado.id,estado = 'X')
                else:
                    creditos = CREDITOS.objects.filter(oficina_id = 1,socio_id = asociado.id).exclude(estado='C')
                for  credito in creditos:
                    results.append({'subcuenta': credito.cod_cre ,'nombre': tercero.nombre.rstrip(),
                        'fec_des' : credito.fec_des,'cap_ini' : credito.cap_ini,'val_cuo':credito.val_cuo_act,
                        'tip_con':concepto.tip_sis})
    elif concepto.tip_sis == '5':
        for tercero in terceros:
            results.append({'subcuenta': tercero.doc_ide,'nombre': tercero.nombre.rstrip()})
    elif concepto.tip_sis == '6':
        cxcs = (
            CXC_DET.objects
                .filter(
                    cuenta_x_cobrar__concepto__cod_con=cod_con  # Filtra por co.cod_con = 'OLIVO'
                )
                .filter(
                    Q(cuenta_x_cobrar__tercero__nombre__icontains=filtro) |  # LIKE '%CAST%'
                    Q(cuenta_x_cobrar__tercero__doc_ide__icontains=filtro)   # LIKE '%CAST%'
                )
                .values('cuenta_x_cobrar__cod_cxc')
                .annotate(total_valor=Sum('valor'))
                .filter(total_valor__gt=0)  # HAVING SUM(cxd.valor) > 0
        )
        for cxc in cxcs :
            cxcsel = CTAS_X_COBRAR.objects.filter(cod_cxc = cxc['cuenta_x_cobrar__cod_cxc']).first()
            results.append({'subcuenta':cxcsel.cod_cxc , 'nombre': cxcsel.tercero.nombre,'valor':cxc['total_valor'],'tip_con':'6' })
    return JsonResponse(results, safe=False)

from justo_app.justo_ahorros import ahorros
from datetime import date
from aportes_app.views import saldo_aportes_fecha

    
def validar_concepto_subcuenta(request):
    cliente_id = request.session.get('cliente_id')  # Obtiene el valor de 'cliente_id' en la sesión
    oficina_id = request.session.get('oficina_id')  # Obtiene el valor de 'oficina_id' en la sesión
    per_con = request.session.get('per_con') 
    hoy = date.today()  # Obtiene la fecha actual
    hoy_formato = hoy.strftime('%Y-%m-%d') 

    cod_con = request.GET.get('cod_con')
    sub_cuenta = request.GET.get('sub_cuenta')
    concepto = CONCEPTOS.objects.filter(cliente_id = 1,cod_con = cod_con).first()
    saldo = 0
    results = []
    if concepto == None:
        return JsonResponse(results, safe=False)
    if concepto.tip_sis == '1':
        asociado = ASOCIADOS.objects.filter(oficina_id = oficina_id,cod_aso=sub_cuenta).first()
        if asociado != None:
            result = saldo_aportes_fecha(sub_cuenta,oficina_id,hoy_formato)
            if result:  # Verifica si result no es None
                saldo = result.Aporte_fecha 
            else:
                saldo = 0  # O cualquier valor predeterminado que desees usar
            tercero = TERCEROS.objects.filter(cliente_id = 1,doc_ide = asociado.cod_aso).first()          
            if tercero != None:
                results.append({'subcuenta': asociado.cod_aso , 'nombre': tercero.nombre.rstrip(),'saldo' : saldo})
    elif concepto.tip_sis == '2':
        cta_ahorro = CTAS_AHORRO.objects.filter(oficina_id = oficina_id,num_cta = sub_cuenta).first()
        if cta_ahorro != None:
            miCtaAho = ahorros(oficina_id,hoy_formato)
            miCtaAho.saldo_cta(sub_cuenta, hoy_formato)
            saldo = -miCtaAho.saldo_fecha 
            asociado = ASOCIADOS.objects.filter(oficina_id = oficina_id,id = cta_ahorro.asociado_id).first()
            if asociado != None:
                tercero = TERCEROS.objects.filter(cliente_id = oficina_id,doc_ide = asociado.cod_aso).first()
                if tercero != None:
                    results.append({'subcuenta': cta_ahorro.num_cta, 'nombre': tercero.nombre.rstrip(),'saldo' : saldo})
    elif concepto.tip_sis == '3':
        credito = CREDITOS.objects.filter(oficina_id = oficina_id,cod_cre = sub_cuenta).exclude(estado='C').first()
        if credito != None:
            asociado = ASOCIADOS.objects.filter(oficina_id = oficina_id,id=credito.socio_id).first()
            if asociado != None:
                tercero = TERCEROS.objects.filter(cliente_id = oficina_id,doc_ide = asociado.cod_aso).first()
                if tercero != None:
                    results.append({'subcuenta': credito.cod_cre ,'nombre': tercero.nombre.rstrip(),'saldo' : saldo})
    elif concepto.tip_sis == '4':
        ctaCon = PLAN_CTAS.objects.filter(cliente_id = cliente_id,cod_cta = sub_cuenta,per_con = per_con).exclude(tip_cta = 'C').first()
        if ctaCon != None:
            results.append({'subcuenta': ctaCon.cod_cta.rstrip(),'nombre': ctaCon.nom_cta.rstrip(),'saldo' : saldo})
    elif concepto.tip_sis == '5' or concepto.tip_sis == '7': 
        print('Entra a valirar tipo 5')
        tercero = TERCEROS.objects.filter(cliente_id = 1,doc_ide = sub_cuenta).first()
        if tercero != None:
            results.append({'subcuenta': tercero.doc_ide , 'nombre': tercero.nombre.rstrip(),'saldo' : saldo})
    elif concepto.tip_sis == '6':
        cxc = CTAS_X_COBRAR.objects.filter(oficina_id = 1,cod_cxc = sub_cuenta).first()
        if cxc != None:
            tercero = TERCEROS.objects.filter(id = cxc.tercero_id).first()
            if tercero != None:
                results.append({'subcuenta': sub_cuenta , 'nombre': tercero.nombre.rstrip(),'saldo' : saldo})
    print('Sakida',results)
    return JsonResponse(results, safe=False)



def buscar_beneficiarios(request):
    query = request.GET.get('query', '')
    if query:
        terceros = TERCEROS.objects.filter(Q(cliente_id = 1) & (Q(nombre__icontains=query) | Q(doc_ide__icontains=query)))[:100]  # Limita a 10 resultados
        results = [{'cedula': ter.doc_ide , 'nombre': ter.nombre.rstrip()} for ter in terceros]
    else:
        results = []
    return JsonResponse(results, safe=False)

def buscar_conceptos(request):
    query = request.GET.get('query', '')
    if query:
        conceptos = CONCEPTOS.objects.filter(Q(cliente_id = 1) & (Q(cod_con__icontains=query) | Q(descripcion__icontains=query)))[:50]  # Limita a 10 resultados
        results = [{'cod_con': concep.cod_con , 'descripcion': concep.descripcion} for concep in conceptos]
    else:
        results = []
    return JsonResponse(results, safe=False)


def index(request):
    return render(request,'index.html')

def get_documentos(request,agno):
    doctos = list(DOCTO_CONTA.objects.filter(oficina_id = 1,per_con = agno).values())
    #print(doctos)
    if (len(doctos) > 0):
        data = {'message':'Correcto','doctos' : doctos}
    else:
        data = {'message':'Errado','doctos' : doctos}
    return JsonResponse(data)

def get_comprobantes(request,docto_id):
    compros = list(HECHO_ECONO.objects.filter(docto_conta_id = docto_id).values())
    if (len(compros) > 0):
        data = {'message':'Correcto','doctos' : compros}
    else:
        data = {'message':'Errado','doctos' : compros}
    return JsonResponse(data)

def get_canales(request):
    lista_canales = [{'codigo': canal, 'nombre': nombre} for canal, nombre in OPC_CANALES]
    if (len(lista_canales) > 0):
        data = {'message':'Correcto','canales' : lista_canales}
    else:
        data = {'message':'Errado','canales' : lista_canales}
    return JsonResponse(data)

def get_ciudades(request):
    localidades = list(LOCALIDADES.objects.filter(cliente_id = 1).values('id','nombre','departamento'))
    if (len(localidades) > 0):
        data = {'message':'Correcto','localidades' : localidades}
    else:
        data = {'message':'Errado','localidades' : localidades}
    return JsonResponse(data)

def get_bancos(request):
    bancos = list(PLAN_CTAS.objects.filter(per_con=2024, tip_cta='A', cta_ban='S').values('id', 'nom_cta'))
    if (len(bancos) > 0):
        data = {'message':'Correcto','bancos' : bancos}
    else:
        data = {'message':'Errado','bancos' : bancos}
    return JsonResponse(data)


#  ---------------------------------------------------------------------------------------------------------------------

from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from .forms_old import HechoEconoForm, DetalleProdForm

# views.py

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms_old import HechoEconoForm, DetalleProdForm

# views.py

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms_old import HechoEconoForm, DetalleProdForm
from django.views.generic import DetailView
from django.db import transaction

    
class HechoEconoUpdateView(UpdateView):
    # Vista para actualizar un HECHO_ECONO existente
    model = HECHO_ECONO
    form_class = HechoEconoForm
    template_name = 'hecho_econo_form.html'

class DetalleProdCreateView(CreateView):
    # Vista para agregar un DETALLE_PROD a un HECHO_ECONO existente
    model = DETALLE_PROD
    form_class = DetalleProdForm
    template_name = 'detalle_prod_form.html'

    def get_success_url(self):
        return reverse_lazy('hecho_econo_detail', kwargs={'pk': self.kwargs['hecho_econo_id']})

class DetalleProdUpdateView(UpdateView):
    # Vista para actualizar un DETALLE_PROD existente
    model = DETALLE_PROD
    form_class = DetalleProdForm
    template_name = 'detalle_prod_form.html'

class DetalleProdDeleteView(DeleteView):
    # Vista para eliminar un DETALLE_PROD existente
    model = DETALLE_PROD
    success_url = reverse_lazy('hecho_econo_list')  # Redireccionar a la lista de HECHO_ECONO después de eliminar
    template_name = 'detalle_prod_confirm_delete.html'

class HechoEconoListView(ListView):
    # Vista para listar todos los HECHO_ECONO
    model = HECHO_ECONO
    template_name = 'hecho_econo_list.html'

class HechoEconoDetailView(DetailView):
    # Vista para ver detalles de un HECHO_ECONO, incluyendo los DETALLE_PROD asociados
    model = HECHO_ECONO
    template_name = 'hecho_econo_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalle_list'] = DETALLE_PROD.objects.filter(hecho_econo=self.object)
        return context
    
class DetalleProdListView(ListView):
    # Vista para listar los DETALLE_PROD asociados a un HECHO_ECONO
    model = DETALLE_PROD
    template_name = 'detalle_prod_list.html'
    context_object_name = 'detalle_list'

    def get_queryset(self):
        hecho_econo_id = self.kwargs['hecho_econo_id']
        hecho_econo = get_object_or_404(HECHO_ECONO, pk=hecho_econo_id)
        return DETALLE_PROD.objects.filter(hecho_econo=hecho_econo)


class DetalleProdFilterView(ListView):
    # Vista para filtrar los DETALLE_PROD por texto
    model = DETALLE_PROD
    template_name = 'detalle_prod_filter.html'
    context_object_name = 'detalle_list'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return DETALLE_PROD.objects.filter(
            Q(concepto__icontains=query) |
            Q(subcuenta__icontains=query) |
            Q(valor__icontains=query)
        )
