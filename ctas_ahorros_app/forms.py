from django.shortcuts import render
from django import forms
from lineas_ahorro_app.models import LINEAS_AHORRO
from asociados_app.models import ASOCIADOS
from .models import CTAS_AHORRO

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column

class CtasAhorroForm(forms.ModelForm):
    num_cta = forms.CharField(label="Número de Cuenta", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    cod_imp = forms.CharField(label="codigo imputacion", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    cod_aso = forms.CharField(label="Código Asociado", max_length=12)

    class Meta:
        model = CTAS_AHORRO
        fields = ['lin_aho', 'num_cta','cod_aso','fec_apertura', 'fec_cancela', 'est_cta', 'exc_tas_mil', 'fec_ini_exc','cod_imp']
        widgets = {
            'fec_apertura': forms.DateInput(attrs={'type': 'date'}),
            'fec_cancela': forms.DateInput(attrs={'type': 'date'}),
            'fec_ini_exc': forms.DateInput(attrs={'type': 'date'}),
            'asociado': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        oficina_id = kwargs.pop('oficina_id', None)
        per_con = kwargs.pop('per_con', None)
        super(CtasAhorroForm, self).__init__(*args, **kwargs)
        if cliente_id and oficina_id and per_con:
            lin_aho_queryset = LINEAS_AHORRO.objects.filter(cliente_id=cliente_id)
            lin_aho_choices = [(la.id, f'{la.cod_lin_aho} - {la.nombre}') for la in lin_aho_queryset]
            self.fields['lin_aho'].choices = lin_aho_choices


   