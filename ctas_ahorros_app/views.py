import json, re, os
import pandas as pd
from openpyxl import Workbook
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from reportlab.pdfgen import canvas
from django import forms
from django.db.models import Max, IntegerField, Func, F, Q, Sum, Min, Value, FloatField, Case, When
from django.db.models.functions import Cast, Coalesce
from django.views.decorators.http import require_GET
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from datetime import datetime, date, timedelta
from django.core.paginator import Paginator

from detalle_economico_app.models import DETALLE_PROD
from terceros_app.models import TERCEROS
from asociados_app.models import ASOCIADOS
from ctas_ahorros_app.models import CTAS_AHORRO
from lineas_ahorro_app.models import LINEAS_AHORRO
from .models import CTAS_AHORRO
from .forms import CtasAhorroForm

# Asegúrate de tener la función get_max_consecutive_for_line en el mismo archivo o importarla
def get_max_consecutive_for_line(id_lin):   
    lin_aho = LINEAS_AHORRO.objects.filter(id=id_lin).first()
    queryset = CTAS_AHORRO.objects.filter(lin_aho=lin_aho)
    queryset = queryset.annotate(
        consecutive_number=Cast(
            Func(
                F('num_cta'),
                function='SUBSTRING',
                template="SUBSTRING(%(expressions)s FROM 4 FOR 6)",  # Desde el carácter 4 por 6 posiciones
                output_field=IntegerField()
            ),
            output_field=IntegerField()
        )
    )
    max_consecutive = queryset.aggregate(max_consecutive=Max('consecutive_number'))['max_consecutive']+1
    if max_consecutive is None:
        max_consecutive = 0
    max_consecutive_str = str(max_consecutive).zfill(6)
    max_value = f"{lin_aho.cod_lin_aho}-{max_consecutive_str}"
    return max_value

@require_GET
def max_consecutivo_view(request):
    line_code = request.GET.get('lin_aho_id')  # Recibimos lin_aho_id desde la URL
    if not line_code:
        return JsonResponse({'error': 'No se recibió ningún código de línea.'}, status=400)
    
    max_consecutivo = get_max_consecutive_for_line(line_code)
    
    if max_consecutivo is not None:
        response = {
            'id_lin_aho': line_code,
            'max_consecutivo': max_consecutivo
        }
    else:
        response = {
            'id_lin_aho': line_code,
            'error': 'No se encontraron registros para esta línea.'
        }
    
    return JsonResponse(response)

class BuscarCtaAhoView(View):
    def get(self, request):
        num_cta = request.GET.get('num_cta', '')
        nombre = request.GET.get('nombre', '')
        est_cta = request.GET.get('est_cta', None)  # Permitir que sea None
        doc_ide = request.GET.get('doc_ide',None)
        resultados = CTAS_AHORRO.objects.all()
        if num_cta:
            resultados = resultados.filter(num_cta__icontains=num_cta)
        if nombre:
            resultados = resultados.filter(asociado__tercero__nombre__icontains=nombre)
        if doc_ide:
            resultados = resultados.filter(asociado__tercero__doc_ide__icontains=doc_ide)    
        if est_cta:  # Solo filtrar si est_cta no es None
            resultados = resultados.filter(est_cta=est_cta)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = list(resultados.values("num_cta", "asociado__tercero__nombre", "est_cta"))
            return JsonResponse(data, safe=False)

        # Si es una petición normal, devolver HTML
        context = {
            'resultados': resultados,
            'num_cta': num_cta,
            'nombre': nombre,
            'est_cta': est_cta,
        }
        return render(request, 'lista_cta_aho.html', context)

class CtasAhorroListView(ListView):
    model = CTAS_AHORRO
    template_name = 'lista_cta_aho.html'
    context_object_name = 'cuentas'
    paginate_by = 10  # Puedes ajustar el número de resultados por página

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = CTAS_AHORRO.objects.all()

        if query:
            object_list = object_list.filter(
                Q(num_cta__icontains=query) | Q(asociado__nombre__icontains=query)
            )

        return object_list
    
class CtasAhorroBaseView(View):
    template_name = 'lista_cta_aho.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cta_aho = self.get_object() if 'pk' in self.kwargs else None
        if cta_aho:  # Si existe un objeto, estamos en modo actualización
            form = self.form_class(instance=cta_aho)
            context['cod_soc'] = cta_aho.asociado.cod_aso if cta_aho.asociado else 'No disponible'
            context['asociado_nombre'] = cta_aho.asociado.tercero.nombre if cta_aho.asociado and cta_aho.asociado.tercero else 'Desconocido'
            context['operation'] = 'update'
            context['button_text'] = 'Modificar'
        else:  # Si no hay objeto, estamos en modo creación
            form = self.form_class()
            context['operation'] = 'create'
            context['button_text'] = 'Guardar'
        context['form'] = form  # Asigna el formulario al contexto
        return context

#    def get_object(self):
#        return get_object_or_404(self.model, id=self.kwargs['pk']) if 'pk' in self.kwargs else None


    def validate_models(self, form):
        errors = {}
        fec_apertura = form.cleaned_data.get('fec_apertura')
        if not self.is_valid_date_format(fec_apertura):
            errors['fec_apertura'] = 'La fecha debe estar en formato dd/mm/yyyy.'
        est_cta = form.cleaned_data.get('est_cta')
        cod_aso = form.cleaned_data.get('cod_aso')
        if not cod_aso :
            errors['cod_aso'] = 'Debe Existir el documento del asociado Titular de la Cuenta.'
        if est_cta == 'C':
            fec_cancela = form.cleaned_data.get('fec_cancela')
            if not self.is_valid_date_format(fec_cancela):
                errors['fecha cancelacion'] = 'cuando el estado es Cancelada, debe diligenciarse este campo.'
            else:
                if fec_cancela < fec_apertura:
                    errors['fecha cancelacion'] = 'La fecha de Cancelacion debe ser posterior a la fecha de Apertura.'
        exc_tas_mil = form.cleaned_data.get('exc_tas_mil')
        fec_ini_exc = form.cleaned_data.get('fec_ini_exc')
        if exc_tas_mil == 'S':
            if not self.is_valid_date_format(fec_ini_exc):
                errors['fec_ini_exc'] = 'cuando la cuenta esta excenta debe indicarse la Fecha Exención.'
            else:
                if fec_ini_exc < fec_apertura:
                    errors['fecha cancelacion1'] = 'La fecha inicial de excencion debe ser igual o posterior a la fecha de Apertura.'
        lin_aho = form.cleaned_data.get('lin_aho')
        if not lin_aho:
            errors['lin_aho'] = 'Debe seleccionar una linea de ahorro.'
        else:
            # Verifica que el valor seleccionado sea un objeto válido en la base de datos
            try:
                get_object_or_404(LINEAS_AHORRO, pk=lin_aho.id)
            except ValidationError:
                errors['lin_aho'] = 'la Liea de Ahorro no es valida.'
        
        return errors

    def is_valid_date_format(self,date_value):
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
        print('Importante saber si pasa por aqui')
        try:
            with transaction.atomic():
                # Guarda el modelo principal HechoEcono
                CTAS_AHORRO = form.save(commit=False)
                CTAS_AHORRO.save()
                self.save_or_update_details(CTAS_AHORRO.id, form)
                self.save_or_update_accounting_details(CTAS_AHORRO, form)
        except Exception as e:
            # Maneja cualquier error que pueda ocurrir durante el guardado
            raise e

    def handle_errors(self, errors):
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        return None
                           
class CtasAhorroCreateView(CtasAhorroBaseView,CreateView):
    model = CTAS_AHORRO
    form_class = CtasAhorroForm
    template_name = 'ctas_ahorro_form.html'
    success_url = reverse_lazy('ctas_ahorro_list')

    def form_valid(self, form):
        lin_aho = form.cleaned_data['lin_aho']
        ultimo_num = CTAS_AHORRO.objects.filter(num_cta__startswith=f"{lin_aho.cod_lin_aho}-").count()
        form.instance.num_cta = f"{lin_aho.cod_lin_aho}-{ultimo_num + 1}"
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)  # Esto llama a get_context_data
        return response

    def post(self, request):
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        cliente_id = self.request.session.get('cliente_id')
        oficina_id = self.request.session.get('oficina_id')
        per_con = self.request.session.get('per_con')
        form = CtasAhorroForm(request.POST)
        cod_aso = request.POST.get('cod_aso')
        asociado = ASOCIADOS.objects.filter(oficina_id = oficina_id,cod_aso = cod_aso).first()
        if asociado:
            form.instance.asociado = asociado  
        if form.is_valid():
            errors = self.validate_models(form)
            if errors:
                error_messages = [f"{key}: {value}" for key, value in errors.items()]       
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': error_messages}, status=200)
                else:
                    messages.error(request, 'Errores en el formulario.')
                    return render(request, 'hecho_econo_form.html', {'form': form})
            cta_ahorro = form.save(commit=False)
            cta_ahorro.oficina_id = oficina_id
            cta_ahorro.asociado = asociado 
            cta_ahorro.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'num_cta': cta_ahorro.num_cta,
                    'mensaje': 'La cuenta se ha grabado exitosamente.',
                    'mostrar_boton_imprimier': True, 
                }, status=200)
           
            else:
                messages.success(request, 'Cuenta de ahorro guardada correctamente. Num_cta -->'+cta_ahorro.num_cta)
                return redirect('nombre_de_la_vista')  # Redirige a otra vista si no es una solicitud AJAX
        else:
            return JsonResponse({'success': False, 'errors': ['Método no permitido']}, status=405)
        
class CtasAhorroUpdateView(CtasAhorroBaseView,UpdateView):
    model = CTAS_AHORRO
    form_class = CtasAhorroForm
    template_name = 'ctas_ahorro_form.html'
    success_url = reverse_lazy('ctas_ahorro_list')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  # Asegúrate de asignar el objeto
        context = self.get_context_data(object=self.object)
        context['pk'] = self.kwargs.get('pk')
        if self.object.asociado:
            context['cod_soc'] = self.object.asociado.cod_aso if self.object.asociado else 'No disponible'
            context['asociado_nombre'] = self.object.asociado.tercero.nombre if self.object.asociado.tercero else 'Desconocido'
        else:
            context['cod_soc'] = 'No disponible'
            context['asociado_nombre'] = 'Desconocido'
        return render(request, self.template_name, context)

    def form_valid(self, form):
        lin_aho = form.cleaned_data['lin_aho']
#        ultimo_num = CTAS_AHORRO.objects.filter(num_cta__startswith=f"{lin_aho.cod_lin_aho}-").count()
#        form.instance.num_cta = f"{lin_aho.cod_lin_aho}-{ultimo_num + 1}"
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        pk = self.kwargs.get('pk')
        print('Entra a post Update ---->')
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        cliente_id = self.request.session.get('cliente_id')
        oficina_id = self.request.session.get('oficina_id')
        per_con = self.request.session.get('per_con')
        form = CtasAhorroForm(request.POST)
        cod_aso = request.POST.get('cod_aso')
        asociado = ASOCIADOS.objects.filter(oficina_id = oficina_id,cod_aso = cod_aso).first()
        if asociado:
            form.instance.asociado = asociado  
        if form.is_valid():
            errors = self.validate_models(form)
            print('errores --->',errors)
            if errors:
                error_messages = [f"{key}: {value}" for key, value in errors.items()]       
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': error_messages}, status=200)
                else:
                    messages.error(request, 'Errores en el formulario.')
                    return render(request, 'hecho_econo_form.html', {'form': form})
            
            cta_ahorro = form.save(commit=False)
            cta_ahorro.id = pk 
            print('cta_ahorro ---> ',cta_ahorro.id)
            print('cta_ahorro ---> ',cta_ahorro.num_cta)
            print('cta_ahorro ---> ',cta_ahorro.fec_ini_exc)

            cta_ahorro.oficina_id = oficina_id
            cta_ahorro.asociado = asociado 
            cta_ahorro.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'num_cta': cta_ahorro.num_cta,
                    'mensaje': 'La cuenta se ha grabado exitosamente.',
                    'mostrar_boton_imprimier': True, 
                }, status=200)
           
            else:
                messages.success(request, 'Cuenta de ahorro guardada correctamente. Num_cta -->'+cta_ahorro.num_cta)
                return redirect('nombre_de_la_vista')  # Redirige a otra vista si no es una solicitud AJAX

        else:
            return JsonResponse({'success': False, 'errors': ['Método no permitido']}, status=405)

class CtasAhorroDeleteView(DeleteView):
    model = CTAS_AHORRO
    template_name = 'ctas_ahorro_confirm_delete.html'
    success_url = reverse_lazy('ctas_ahorro_list')

class ImprimirPDF(View):
    def get(self, request, *args, **kwargs):
        # Recupera los datos de la base de datos
        # Asegúrate de adaptar esto a tu modelo y consulta específicos
        cta_ahos = CTAS_AHORRO.objects.all()

        # Creamos un objeto HttpResponse con el tipo de contenido PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="cta_ahos.pdf"'

        # Creamos un objeto PDF con ReportLab
        p = canvas.Canvas(response)

        # Agregamos contenido al PDF utilizando datos de la base de datos
        for dato in cta_ahos:
            p.drawString(80, 800, f"Oficina: {dato.oficina}")
            p.drawString(80, 780, f"Línea de Ahorro: {dato.lin_aho}")
            p.drawString(80, 760, f"Nombre Asociado: {dato.asociado}")
            p.drawString(80, 740, f"Número Cuenta: {dato.num_cta}")
            p.drawString(80, 720, f"Estado Cuenta: {dato.est_cta}")
            p.drawString(80, 700, f"Fecha Apertura: {dato.fec_apertura}")
            p.drawString(80, 680, f"Fecha Cancelación: {dato.fec_cancela}")
            p.drawString(80, 660, f"Exenta 4x1000?: {dato.exc_tas_mil}")
            p.drawString(80, 640, f"Fecha Exención: {dato.fec_ini_exc}")
            
            # Agrega más campos según tus necesidades

            # Agrega un salto de página para el siguiente conjunto de datos
            p.showPage()

        # Cierra el objeto PDF y devuelve la respuesta
        p.save()

        return response

# Para imprimir un registro
class ImprimePDF(View):
    def get(self, request, pk, *args, **kwargs):
        # Recupera los datos de la base de datos
        # Asegúrate de adaptar esto a tu modelo y consulta específicos
        dato = CTAS_AHORRO.objects.get(pk=pk)

        # Creamos un objeto HttpResponse con el tipo de contenido PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="cta_ahos.pdf"'

        # Creamos un objeto PDF con ReportLab
        p = canvas.Canvas(response)

        # Agregamos contenido al PDF utilizando datos de la base de datos
        p.drawString(80, 800, f"Oficina: {dato.oficina}")
        p.drawString(80, 780, f"Línea de Ahorro: {dato.lin_aho}")
        p.drawString(80, 760, f"Nombre Asociado: {dato.asociado}")
        p.drawString(80, 740, f"Número Cuenta: {dato.num_cta}")
        p.drawString(80, 720, f"Estado Cuenta: {dato.est_cta}")
        p.drawString(80, 700, f"Fecha Apertura: {dato.fec_apertura}")
        p.drawString(80, 680, f"Fecha Cancelación: {dato.fec_cancela}")
        p.drawString(80, 660, f"Exenta 4x1000?: {dato.exc_tas_mil}")
        p.drawString(80, 640, f"Fecha Exención: {dato.fec_ini_exc}")

        # Agrega más campos según tus necesidades

        # Agrega un salto de página para el siguiente conjunto de datos
        p.showPage()

        # Cierra el objeto PDF y devuelve la respuesta
        p.save()

        return response

class ExportarView(View):
    template_name = 'exportar.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        export_type = request.POST.get('export_type')

        if export_type == 'pdf':
            return self.exportar_pdf()
        elif export_type == 'excel':
            return self.exportar_excel()
        elif export_type == 'csv':
            return self.exportar_csv()

    def exportar_pdf(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="exportacion.pdf"'
        cta_ahos = CTAS_AHORRO.objects.all()

        p = canvas.Canvas(response)

        for dato in cta_ahos:
            p.drawString(80, 800, f"Oficina: {dato.oficina}")
            p.drawString(80, 780, f"Línea de Ahorro: {dato.lin_aho}")
            p.drawString(80, 760, f"Nombre Asociado: {dato.asociado}")
            p.drawString(80, 740, f"Número Cuenta: {dato.num_cta}")
            p.drawString(80, 720, f"Estado Cuenta: {dato.est_cta}")
            p.drawString(80, 700, f"Fecha Apertura: {dato.fec_apertura}")
            p.drawString(80, 680, f"Fecha Cancelación: {dato.fec_cancela}")
            p.drawString(80, 660, f"Exenta 4x1000?: {dato.exc_tas_mil}")
            p.drawString(80, 640, f"Fecha Exención: {dato.fec_ini_exc}")

            # Agrega más campos según tus necesidades

            # Agrega un salto de página para el siguiente conjunto de datos
            p.showPage()
        # Puedes agregar más contenido según tus necesidades.
        p.save()

        return response

    def exportar_excel(self):
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="exportacion.xlsx"'

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Datos"

        # Añade encabezados a la hoja de cálculo utilizando los nombres de campo del modelo
        headers = [field.name for field in CTAS_AHORRO._meta.fields]
        for col_num, header in enumerate(headers, 1):
            sheet.cell(row=1, column=col_num, value=header)

        # Añade datos a la hoja de cálculo
        cta_ahos = CTAS_AHORRO.objects.all()
        for row_num, data in enumerate(cta_ahos, start=2):
            for col_num, field in enumerate(headers, 1):
                sheet.cell(row=row_num, column=col_num,
                           value=getattr(data, field))

        workbook.save(response)
        return response

    def exportar_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="exportacion.csv"'

        writer = csv.writer(response)
        # Añade más encabezados según tus necesidades
        writer.writerow(['ID', 'Nombre'])

        cta_ahos = CTAS_AHORRO.objects.all()
        for data in cta_ahos:
            # Añade más campos según tus necesidades
            writer.writerow([data.pk, data.nombre])

        return response

def liquidar_ctas_ahorro(request):
    if request.method == 'POST':
        fecha_corte_str = request.POST.get('fecha_corte')
        nombre_archivo = request.POST.get('nombre_archivo')
        liquidar_ahorros_process(fecha_corte_str, nombre_archivo, request)
        try:
            return JsonResponse({'message': 'Cálculos de liquidación iniciados.'})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return render(request, 'saldos_cuentas.html')
    
def liquidar_ahorros_process(fecha_corte_str, nombre_archivo, request):
    fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
    if not os.path.exists(os.path.dirname(nombre_archivo)):
        raise ValueError("El directorio especificado no existe.")
    
    resultados = []
    print('Hora de Inicio ',datetime.now(),'  archivo  ',nombre_archivo)
    result= (
        DETALLE_PROD.objects.filter(
            producto = 'AH',
            hecho_econo__fecha__lte= fecha_corte,
            hecho_econo__docto_conta__oficina_id = 1
        )
        .values('subcuenta')  # Agrupamos por 'subcuenta'
        .annotate(
            cod_cta = F('subcuenta'),
            saldo_fecha = -Sum(F('valor')),  # Negamos la suma como en la SQL
            fec_ult_mov = Max('hecho_econo__fecha'),
            fec_pri_mov = Min('hecho_econo__fecha')
        )
    )
    result_list = list(result)
    nun_ctas = 0
    for item in result_list:
        if item['cod_cta'] is not None or item['fec_ult_mov'] is not None:
            cta_aho = CTAS_AHORRO.objects.filter(num_cta = item['cod_cta'],oficina_id = 1).first()
            asociado = ASOCIADOS.objects.filter(oficina_id = 1,id = cta_aho.asociado_id).first()
            if asociado == None:
                continue
            if asociado.tercero_id == None:
                print('Error de Integridad cod_aso ',asociado.cod_aso)
                continue
            tercero = TERCEROS.objects.filter(id = asociado.tercero_id).first()
            if tercero != None:
                nun_ctas = nun_ctas + 1
                resultados.append({
                    'cod_cta' : item['cod_cta'],
                    'nombre' : tercero.nombre,
                    'doc_ide' : tercero.doc_ide,
                    'saldo_fecha' : item['saldo_fecha'],
                    'fec_pri_mov' : item['fec_pri_mov'],
                    'fec_ult_mov' : item['fec_ult_mov']
                })

    print('Hora de Final  ',datetime.now())    
    df = pd.DataFrame(resultados)
    print('df ya    ',datetime.now())    
    # df.to_excel(nombre_archivo, index=False)
    #df.to_excel(nombre_archivo, index=False, engine='xlsxwriter')
    df.to_excel(nombre_archivo, index=False, engine='openpyxl')
    print(df.head())
    print('a excel  ',datetime.now())    
    return(nun_ctas)

#  ------------------------------------------------------------------------------------------------ 

def ejecutar_consulta_orm(oficina_id,subcuenta,fecha_ini,fecha_fin):
    # Primera parte de la consulta
    saldo_anterior = DETALLE_PROD.objects.filter(
        producto = 'AH',
        subcuenta = subcuenta,
        hecho_econo__fecha__lt = fecha_ini, 
        hecho_econo__docto_conta__oficina_id=oficina_id
    ).aggregate(
        Saldo=Coalesce(-Sum('valor'), 0, output_field = FloatField())
    )
    resultado_saldo_anterior = {
        'Fecha' : fecha_ini - timedelta(days = 1),
        'Comprobante' : 'Saldo Anterior',
        'Numero' : 0,
        'Concepto': '',
        'Consignacion' : 0,
        'Retiro' : 0,
        'Saldo' : saldo_anterior['Saldo']
    }
    
    # Segunda parte de la consulta
    movimientos = DETALLE_PROD.objects.filter(
        producto = 'AH',
        subcuenta = subcuenta,
        hecho_econo__fecha__range = (fecha_ini, fecha_fin),
        hecho_econo__docto_conta__oficina_id=oficina_id
    ).annotate(
        Fecha = F('hecho_econo__fecha'),
        Comprobante = F('hecho_econo__docto_conta__nom_cto'),
        Numero = F('hecho_econo__numero'),
        Concepto = F('concepto'),
        Consignacion = Case(
            When(valor__lt = 0, then = -F('valor')),
            default = Value(0),
            output_field = FloatField()
        ),
        Retiro=Case(
            When(valor__gt = 0, then = F('valor')),
            default = Value(0),
            output_field = FloatField()
        ),
        Saldo = Value(0, output_field = FloatField())
    ).values(
        'Fecha', 'Comprobante', 'Numero', 'Concepto', 'Consignacion', 'Retiro', 'Saldo'
    ).order_by('Fecha')

    # Unir las dos partes
    resultados = [resultado_saldo_anterior] + list(movimientos)    
    return resultados

def obtener_titular_cta_aho(request, num_cta):
    CtaAho = CTAS_AHORRO.objects.filter(oficina_id = 1,num_cta = num_cta).first()
    if CtaAho:
        nom_titular = CtaAho.asociado.tercero.nombre
        return JsonResponse({"nom_titular": nom_titular})
    return JsonResponse({"nom_titular": ""})  # Devuelve vacío si no encuentra la cuenta

def listar_movtos_cta_ahorro(request, cliente_id=None, oficina_id=None):
    cta_aho = request.GET.get('num_cta', '').strip()
    fecha_ini = request.GET.get('fecha_inicio', None)
    fecha_fin = request.GET.get('fecha_final', None)
    
    # Si viene un nuevo nom_titular en la petición, lo actualizamos en la sesión
    oficina_id = request.session.get('oficina_id')
    
    date_format = "%Y-%m-%d"
    fecha_actual = datetime.now()
    if fecha_ini == None:
        fecha_inicio = datetime(fecha_actual.year - 1, 1, 1).date()
    else:
        fecha_inicio = datetime.strptime(fecha_ini, date_format).date()
    if fecha_fin == None:
        fecha_final = datetime(fecha_actual.year,1,1).date()
    else:
        fecha_final = datetime.strptime(fecha_fin, date_format).date()

    fecha_final = fecha_actual.date()
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_final_str = fecha_final.strftime('%Y-%m-%d')

    print(f"Fecha inicio: {fecha_inicio}, Fecha final: {fecha_final}")

    oficina_id = int(request.GET.get('oficina_id', 1))  # Obtiene el valor de oficina_id de los parámetros GET
    resultados = []
    nom_titular = ''
    if len(cta_aho) > 3: 
        CtaAho = CTAS_AHORRO.objects.filter(oficina_id = oficina_id,num_cta = cta_aho).first()
        if CtaAho == None:
            return render(request, 'lista_movtos_cta_aho.html', {
                'page_obj': page_obj,
                'num_cta': cta_aho,
                'fecha_inicio': fecha_inicio_str,
                'fecha_final': fecha_final_str,
                'nom_titular': nom_titular,  # Se agrega al contexto
            })
        else:
            nom_titular = CtaAho.asociado.tercero.nombre
            resultados = ejecutar_consulta_orm(oficina_id,cta_aho,fecha_inicio,fecha_final)
    else:
        resultados = []
    rows = []
    sal_acu = 0
    for row in resultados:
        sal_acu = sal_acu + float(row['Consignacion']) - float(row['Retiro']) + float(row['Saldo'])
        upd_row = row
        upd_row['Saldo'] = sal_acu
        rows.append(upd_row)
    
    paginator = Paginator(rows, 10)  # 10 resultados por página
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)

    saldo_formateado = "${:,.2f}".format(sal_acu)


    return render(request, 'lista_movtos_cta_aho.html', {
        'context': page_obj,
        'page_obj': page_obj,
        'num_cta': cta_aho,
        'nom_titular': nom_titular,
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_final': fecha_final.strftime('%Y-%m-%d'),
        'saldo_cta': saldo_formateado 
    })

def obtener_fecha_ctas_ahorros(oficina_id,fecha,subcuenta=None,cliente_id=None):
       
    fecha_ahorro = DETALLE_PROD.objects.filter(
            producto='AH',
            concepto='AHO',
            hecho_econo__fecha__lte=fecha,
            subcuenta__in=CTAS_AHORRO.objects.filter(
                oficina_id=oficina_id,
                asociado__tercero__doc_ide=subcuenta,
                asociado__tercero__cliente_id=cliente_id
            ).values_list('num_cta', flat=True)
        ).aggregate(max_fecha=Max('hecho_econo__fecha'))['max_fecha']
    
    return fecha_ahorro if fecha_ahorro else date(2000, 1, 1)
    