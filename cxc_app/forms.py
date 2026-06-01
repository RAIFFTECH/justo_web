from django.shortcuts import render
from django import forms
from lineas_ahorro_app.models import LINEAS_AHORRO
from asociados_app.models import ASOCIADOS
from .models import CTAS_X_COBRAR
from contabilizacion_lineas_ahorros_app.models import IMP_CON_LIN_AHO
from conceptos_app.models import CONCEPTOS
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from django.utils.timezone import now  

class CtasXCobrarForm(forms.ModelForm):
    cod_cxc = forms.CharField()
    fecha_des = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), input_formats=['%d/%m/%Y'])
    fecha_exi = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), input_formats=['%d/%m/%Y'])
    cod_aso = forms.CharField(label="Código Asociado", max_length=12)
    
    class Meta:
        model = CTAS_X_COBRAR
        fields = ['cod_cxc','concepto','valor','fecha_des','fecha_exi','aplicado']
        widgets = {
            'fecha_des': forms.DateInput(attrs={'id': 'fecha','class': 'form-control','type': 'date' }),
            'fecha_exi': forms.DateInput(attrs={'id': 'fecha','class': 'form-control','type': 'date' }),
            'valor': forms.TextInput(attrs={'class': 'form-control currency text-right'})
        }
        
    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        oficina_id = kwargs.pop('oficina_id', None)
        operation  = kwargs.pop('operation', None)
        instance = kwargs.get('instance', None)
        max_value_str = kwargs.pop('max_value_str', None)
        super(CtasXCobrarForm, self).__init__(*args, **kwargs)
        self.fields['aplicado'].widget.attrs['disabled'] = 'disabled'
        self.fields['aplicado'].initial = 'X'  # 
        self.fields['fecha_des'].input_formats = ['%d/%m/%Y', '%Y-%m-%d'] 
        self.fields['fecha_exi'].input_formats = ['%d/%m/%Y', '%Y-%m-%d'] 
        if operation == 'create':
            self.fields['fecha_des'].initial = now().date()
        if instance is None and max_value_str is not None:
            self.fields['cod_cxc'].widget.attrs['value'] = max_value_str
            self.fields['cod_cxc'].widget.attrs['readonly'] = True  # Campo solo lectura
        if cliente_id and oficina_id:
            conceptos_queryset = CONCEPTOS.objects.filter(cliente_id = cliente_id,tip_sis = '6')
            conceptos_choices = [('', 'No asignado')]
            conceptos_choices += [(la.id, f'{la.cod_con} - {la.descripcion}') for la in conceptos_queryset]
            self.fields['concepto'].choices = conceptos_choices
            self.fields['aplicado'].initial = 'X' 


class BusquedaForm(forms.Form):
    concepto = forms.ModelChoiceField(
        queryset=CONCEPTOS.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        super().__init__(*args, **kwargs)
        if cliente_id:
            conceptos_queryset = CONCEPTOS.objects.filter(cliente_id = cliente_id,tip_sis = '6')
            conceptos_choices = [('','No asignado')]
            conceptos_choices += [(la.id, f'{la.cod_con} - {la.descripcion}') for la in conceptos_queryset]
            self.fields['concepto'].choices = conceptos_choices
        else:
            print('desaparecio cliente_id')


class ImportarCxcForm(forms.ModelForm):
    fecha_des = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), input_formats=['%d/%m/%Y'])
    fecha_exi = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), input_formats=['%d/%m/%Y']) 
    excelFile = forms.FileField(label='Subir archivo Excel')   
    class Meta:
        model = CTAS_X_COBRAR
        fields = ['concepto','fecha_des','fecha_exi']
        widgets = {
            'fecha_des': forms.DateInput(attrs={'id': 'fecha','class': 'form-control','type': 'date' }),
            'fecha_exi': forms.DateInput(attrs={'id': 'fecha','class': 'form-control','type': 'date' }),
        }
        
    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        oficina_id = kwargs.pop('oficina_id', None)
        instance = kwargs.get('instance', None)
        super(ImportarCxcForm, self).__init__(*args, **kwargs)
        self.fields['fecha_des'].input_formats = ['%d/%m/%Y', '%Y-%m-%d'] 
        self.fields['fecha_exi'].input_formats = ['%d/%m/%Y', '%Y-%m-%d'] 
        if cliente_id and oficina_id:
            conceptos_queryset = CONCEPTOS.objects.filter(cliente_id = cliente_id,tip_sis = '6')
            conceptos_choices = [('', 'No asignado')]
            conceptos_choices += [(la.id, f'{la.cod_con} - {la.descripcion}') for la in conceptos_queryset]
            self.fields['concepto'].choices = conceptos_choices
        
class EliminarCxcForm(forms.Form):
    excelFile = forms.FileField(label='Subir archivo Excel')   
        
    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        oficina_id = kwargs.pop('oficina_id', None)
        instance = kwargs.get('instance', None)
        super(EliminarCxcForm, self).__init__(*args, **kwargs)
        