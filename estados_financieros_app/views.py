from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django_xhtml2pdf.utils import generate_pdf
from django_xhtml2pdf.views import PdfMixin
from django.views.generic import DetailView
from openpyxl.workbook import Workbook

from terceros_app.models import TERCEROS
from .models import ESTADOS_FIN
from .forms import EstadosForm
from reportlab.pdfgen import canvas


class Lista(LoginRequiredMixin, ListView):
    model = ESTADOS_FIN
    paginate_by = 10
    template_name = 'lista_estados_financieros.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return self.model.objects.filter(Q(cliente__nombre__icontains=query) | Q(tercero__nombre__icontains=query) |
                                             Q(cliente__doc_ide__icontains=query) | Q(tercero__doc_ide__icontains=query)
                                             )
        return self.model.objects.all()


class Detalle(LoginRequiredMixin, DetailView):
    model = ESTADOS_FIN
    template_name = "detalle_estado_financiero.html"


class Crear(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ESTADOS_FIN
    form_class = EstadosForm
    success_url = reverse_lazy('listar_estado_financiero')
    success_message = "Estado financiero creado exitosamente."
    template_name = "crear_estado_financiero.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def get(self, request, *args, **kwargs):
        id_ter = request.GET.get("id_ter")
        if id_ter:
            tercero = TERCEROS.objects.get(id=id_ter)
            self.form_class.base_fields['tercero'].initial = tercero
            self.form_class.base_fields['cliente'].initial = tercero.cliente
        return super().get(request, *args, **kwargs)


class Actualizar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ESTADOS_FIN
    form_class = EstadosForm
    success_url = reverse_lazy('listar_estado_financiero')
    success_message = "Estado financiero actualizado exitosamente"
    template_name = "crear_estado_financiero.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs


class Eliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ESTADOS_FIN
    success_url = reverse_lazy('listar_estado_financiero')
    success_message = "Estado financiero eliminado"

class ExportPDF(PdfMixin, DetailView):
    model = ESTADOS_FIN
    template_name = "pdf-estados-financieros.html"
    context_object_name = "estado"


class ExportExcel(View):
    def get(self, request, *args, **kwargs):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Estados Financieros"

        # Crear los encabezados en la primera fila
        sheet.append([
            "Cliente", "Tercero", "Fecha Información",
            "Ingresos por Salario Fijo", "Ingresos por Honorarios", "Ingresos por Pensión",
            "Ingresos por Arrendamientos", "Ingresos por Comisiones", "Otros Ingresos",
            "Total Ingresos", "Egresos Sector Financiero", "Egresos Cuota Hipotecaria",
            "Egresos Gastos Familiares", "Egresos Otros Créditos", "Egresos por Arriendo",
            "Total Egresos", "Actividad Otros Egresos", "Activos Tipo de Bien",
            "Activos Vehículo", "Otros Activos", "Total Activos", "Activos Finca Raíz",
            "Activos Inversiones", "Matrícula Escritura", "Otros Pasivos", "Pasivo Tipo",
            "Total Patrimonio", "Valor Pasivos", "Total Pasivos", "Pasivos Descuentos",
            "Declara Renta?", "Tipo Pasivo", "Descripción Pasivo", "Valor Pasivo",
            "Oper. Moneda Extranjera?", "Nombre Banco Extranjero", "Oper. País Extranjero?",
            "Oper. Monto Extranjero?", "Núm. Cuenta Extranjero", "Tipo Oper. Extranjero",
            "Monto Oper. Extranjera?", "Producto Moneda Extranjera?",
            "Descripción Producto Extranjero", "Monto Producto Extranjero",
            "País Producto Extranjero", "Ciudad Producto Extranjero",
            "Promedio producto Extranjero", "Tiene Activos de Vivienda?",
            "Tiene Inversiones?", "Tiene otros pasivos?"
        ])

        # Obtener los datos del modelo ESTADOS_FIN
        estados_fin = ESTADOS_FIN.objects.all()

        # Agregar los datos de cada registro a la hoja de cálculo
        for estado in estados_fin:
            sheet.append([
                estado.cliente.nombre if estado.cliente else '',
                estado.tercero.nombre if estado.tercero else '',
                estado.fec_inf.strftime('%Y-%m-%d') if estado.fec_inf else '',
                estado.ing_sal_fij,
                estado.ing_hon,
                estado.ing_pen,
                estado.ing_arr,
                estado.ing_com,
                estado.ing_ext,
                estado.ing_tot,
                estado.egr_sec_fin,
                estado.egr_cuo_hip,
                estado.egr_gas_fam,
                estado.egr_otr_cre,
                estado.egr_arr,
                estado.egr_tot,
                estado.act_otr_egr,
                estado.act_tip_bien,
                estado.act_vei,
                estado.act_otr,
                estado.tot_act,
                estado.act_fin_rai,
                estado.act_inv,
                estado.escritura,
                estado.pas_otr,
                estado.pas_tip,
                estado.tot_pat,
                estado.pas_val,
                estado.tot_pas,
                estado.pas_des,
                estado.dec_ren,
                estado.tip_pas,
                estado.des_pas,
                estado.val_pas,
                estado.ope_mon_ext,
                estado.nom_ban_ext,
                estado.ope_pais_ext,
                estado.ope_monto_ext,
                estado.num_cta_ext,
                estado.tip_ope_ext,
                estado.mon_ope_ext,
                estado.prod_mon_ext,
                estado.des_prod_ext,
                estado.mon_prod_ext,
                estado.pais_prod_ext,
                estado.ciu_prod_ext,
                estado.prom_prod_ext,
                estado.act_vivienda,
                estado.tiene_inversiones,
                estado.otros_pasivos
            ])

        # Preparar la respuesta HTTP para devolver el archivo Excel
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=estados_financieros.xlsx"

        # Guardar el libro de trabajo en la respuesta
        workbook.save(response)

        return response


class ImprimePDF(View):
    def get(self, request, pk, *args, **kwargs):
        estado = ESTADOS_FIN.objects.get(id=pk)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="estados_financieros.pdf"'

        p = canvas.Canvas(response)
        start = 800

        for field in estado._meta.fields:
            p.drawString(60, start, f"{field.verbose_name}: {getattr(estado, field.name)}")
            start -= 20

        p.showPage()

        p.save()

        return response
