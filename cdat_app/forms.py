from django.shortcuts import render
from django import forms
from lineas_ahorro_app.models import LINEAS_AHORRO
from asociados_app.models import ASOCIADOS
from .models import CTAS_AHORRO,CTA_CDAT
from contabilizacion_lineas_ahorros_app.models import IMP_CON_LIN_AHO
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column

class CtasCdatsForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), input_formats=['%d/%m/%Y'])
    fecha_amp = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), input_formats=['%d/%m/%Y'])    
    num_cta = forms.CharField(label="Número de Cuenta", max_length=10, widget=forms.TextInput())
    est_cta = forms.CharField(label="Estado", max_length=1, widget=forms.TextInput())
    cod_aso = forms.CharField(label="Código Asociado", max_length=12)
    plazo_mes_amp = forms.IntegerField(required=False)
    tiae_amp = forms.DecimalField(required=False, max_digits=8, decimal_places=3)
    tiae_amp = forms.DecimalField(required=False, max_digits=8, decimal_places=3, 
                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}))

    
    class Meta:
        model = CTA_CDAT
        fields = ['num_cta','est_cta','imp_con', 'ampliacion','valor','fecha', 'plazo_mes', 'tiae', 'Periodicidad', 'cta_int_ret','aplicado']
        widgets = {
            'fecha': forms.DateInput(attrs={'id': 'fecha','class': 'form-control','type': 'date' }),
            'fecha_amp': forms.DateInput(attrs={'id': 'fecha','class': 'form-control','type': 'date' }),
            'cta_int_ret': forms.TextInput(attrs={'id': 'cta_int_ret','class': 'form-control'}),
            'valor': forms.TextInput(attrs={'class': 'form-control currency text-right'}),
            'valor_amp': forms.TextInput(attrs={'class': 'form-control currency text-right'}),
            'tiea' : forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}), max_digits=8,decimal_places=3),
            'tiea_amp' : forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}), max_digits=8,decimal_places=3),
        }
        
    def __init__(self, *args, **kwargs):
        print('form __init__')
        cliente_id = kwargs.pop('cliente_id', None)
        oficina_id = kwargs.pop('oficina_id', None)
        operation  = kwargs.pop('operation', None)
        instance = kwargs.get('instance', None)
        fecha_inicial = kwargs.pop('fecha_inicial', None)
        fecha_amp_inicial = kwargs.pop('fecha_amp_inicial', None)
        tiae_amp_inicial = kwargs.pop('tiae_amp_inicial', 0) 
        super(CtasCdatsForm, self).__init__(*args, **kwargs)
        self.fields['ampliacion'].widget.attrs['readonly'] = 'readonly'
        self.fields['fecha_amp'].widget.attrs['readonly'] = 'readonly'
        if tiae_amp_inicial is not None:
            self.fields['tiae_amp'].initial = tiae_amp_inicial 
        if instance and instance.cta_aho:
            self.fields['num_cta'].initial = instance.cta_aho.num_cta
            self.fields['est_cta'].initial = instance.cta_aho.est_cta
        self.fields['aplicado'].widget.attrs['disabled'] = 'disabled'
        self.fields['aplicado'].initial = 'N'  # 
        self.fields['fecha'].input_formats = ['%d/%m/%Y', '%Y-%m-%d'] 

        if instance and instance.aplicado:
            self.fields['aplicado'].initial = instance.aplicado
        if fecha_inicial:
            self.fields['fecha'].initial = fecha_inicial
        if fecha_amp_inicial:
            self.fields['fecha_amp'].initial = fecha_amp_inicial
        if tiae_amp_inicial:
            self.fields['tiae_amp'].initial = tiae_amp_inicial
        if cliente_id and oficina_id:
            imp_lin_aho_queryset = IMP_CON_LIN_AHO.objects.filter(linea_ahorro_id = 2)
            imp_lin_aho_choices = [(la.id, f'{la.cod_imp} - {la.descripcion}') for la in imp_lin_aho_queryset]
            self.fields['imp_con'].choices = imp_lin_aho_choices
            self.fields['num_cta'].widget.attrs['readonly'] = 'readonly'
            self.fields['est_cta'].widget.attrs['readonly'] = 'readonly'
            self.fields['aplicado'].initial = 'N'  # Establece el valor inicial como 'N'
            


from django import forms

class ReporteCdatForm(forms.Form):
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha Inicial"
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha Final"
    )
    directorio = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: C:\\Reportes\\'}),
        label="Directorio de destino"
    )
    nombre_archivo = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: reporte.xlsx'}),
        label="Nombre del archivo"
    )



