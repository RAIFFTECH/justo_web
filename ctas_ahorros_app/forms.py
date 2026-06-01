from django.shortcuts import render
from django import forms
from lineas_ahorro_app.models import LINEAS_AHORRO
from asociados_app.models import ASOCIADOS
from .models import CTAS_AHORRO,CANJE_AHORROS
from justo_app.opciones import OPC_BOOL,OPC_EST_CTA_AHO,OPC_CANJE

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from django.forms import DateInput

class CtasAhorroForm(forms.ModelForm):
    #num_cta = forms.CharField(label="Número de Cuenta", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    num_cta = forms.CharField(label="Número de Cuenta")
    cod_imp = forms.CharField(label="codigo imputacion", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    cod_aso = forms.CharField(label="Código Asociado", max_length=12)

    class Meta:
        model = CTAS_AHORRO
        fields = ['lin_aho', 'num_cta','cod_aso','fec_apertura', 'fec_cancela', 'est_cta', 'exc_tas_mil', 'fec_ini_exc','cod_imp']
        widgets = {
            'fec_apertura': DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fec_cancela': DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fec_ini_exc': DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        oficina_id = kwargs.pop('oficina_id', None)
        per_con = kwargs.pop('per_con', None)
        super(CtasAhorroForm, self).__init__(*args, **kwargs)
        self.fields['fec_apertura'].input_formats = ['%Y-%m-%d']
        self.fields['fec_cancela'].input_formats = ['%Y-%m-%d']
        self.fields['fec_ini_exc'].input_formats = ['%Y-%m-%d']
        if cliente_id and oficina_id and per_con:
            lin_aho_queryset = LINEAS_AHORRO.objects.filter(cliente_id=cliente_id)
            lin_aho_choices = [(la.id, f'{la.cod_lin_aho} - {la.nombre}') for la in lin_aho_queryset]
            self.fields['lin_aho'].choices = lin_aho_choices

class CrearForm(forms.ModelForm):
    class Meta:
        model = CTAS_AHORRO
        fields = "__all__"

class CanjeAhorrosFiltroForm(forms.Form):
    num_cta = forms.CharField(label='Número de Cuenta', required=False)
    nombre = forms.CharField(label='Nombre del Usuario', required=False)
    estado = forms.ChoiceField(label='Estado', choices=OPC_CANJE, required=False)
    historico = forms.BooleanField(label='Histórico', required=False, initial=False)   

from datetime import date

class CambioEstadoCanjeForm(forms.Form):
    nuevo_estado = forms.ChoiceField(
        choices=OPC_CANJE,
        label="Nuevo Estado",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    fecha_nueva = forms.DateField(
        label="Fecha Nueva",
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'},
            format='%Y-%m-%d'  # ✅ MUY IMPORTANTE
        ),
        input_formats=['%Y-%m-%d']  # ✅ Para validar correctamente
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields['fecha_nueva'].initial = date.today().strftime('%Y-%m-%d')