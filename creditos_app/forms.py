from django.shortcuts import render
from django import forms
from .models import CREDITOS
from lineas_credito_app.models import LINEAS_CREDITO
from contabilizacion_capital_creditos_app.models import IMP_CON_CRE
from datetime import date,datetime
import datetime
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Field
from django import forms
from datetime import date
from dateutil.relativedelta import relativedelta

class FechaForm(forms.Form):
    fec_de = forms.DateField(label="Fecha", widget=forms.DateInput(attrs={'type': 'date'}))

class CustomDateInput(forms.DateInput):
    input_type = 'date'

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.DateInput):
                field.widget = CustomDateInput()

class CreditoForm(BaseForm):
    doc_ide = forms.CharField(label='Documento de Identidad', required=False)
    nom_soc = forms.CharField(label='Nombre del Socio', required=False)
    cap_ini = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'numeric-field'}))
    val_cuo_ini = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'numeric-field'}),required=False)
    val_cuo_act = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'numeric-field'}),required=False)

    class Meta:
        model = CREDITOS
        fields = [
            'cod_cre',
            'cap_ini',
            'num_cuo_ini',
            'num_cuo_gra',
            'tian_ic_ini',
            'cod_lin_cre',
            'fec_des',
            'decreciente',
            'tian_pol_seg',
            'per_ano',
            'fec_pag_ini',
            'val_cuo_ini',
            'tian_im',
            'imputacion',
            'libranza',
            'pagare',
            'termino',
            'for_pag',
            'tip_gar',
            'por_des_pro_pag',
            'estado',
            'est_jur',
            'rep_cen_rie',
            'figarantias',
            'fec_ult_pag',
            'num_cuo_act',
            'val_cuo_act',
            'val_gar_hip',
            'mat_inm_gar',
            'num_pol_gar_hip',
            'cat_nue',
            'prima',
            'porcentaje_prima'
        ]
        widgets = {
            'fec_des': forms.DateInput(attrs={'type': 'date'}),
            'fec_pag_ini': forms.DateInput(attrs={'type': 'date'}),
            'fec_reem': forms.DateInput(attrs={'type': 'date'}),
            'fec_ven': forms.DateInput(attrs={'type': 'date'}),
            'bitacora': forms.Textarea(attrs={'rows': 4}),
            'cap_ini': forms.TextInput(attrs={'data-type': 'currency'}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        initial_cod_cre = kwargs.pop('initial_cod_cre', None)  # Extrae `initial_cod_cre`
        print('initial_cod_cre  ',initial_cod_cre)
        super().__init__(*args, **kwargs)
        if request:
            cliente_id = request.session.get('cliente_id')
            if cliente_id:
                print('__init__ - Si hay cliente_id:', cliente_id)
                self.fields['imputacion'].queryset = IMP_CON_CRE.objects.filter(cliente_id=cliente_id)
                self.fields['cod_lin_cre'].queryset = LINEAS_CREDITO.objects.filter(cliente_id=cliente_id)
                
            else:
                print('__init__ - NO hay cliente_id')
        if initial_cod_cre:
            self.fields['cod_cre'].initial = initial_cod_cre  # Asigna `new_cod_cre` como valor inicial
        self.fields['cod_cre'].widget.attrs['readonly'] = True
        self.fields['estado'].widget.attrs.update({'readonly': 'readonly'})
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('val_cuo_ini', css_class='highlight-field')
        )
        if not self.instance.pk:  # Si es un nuevo registro
            self.fields['fec_des'].initial = date.today().strftime('%Y-%m-%d')
            self.fields['fec_pag_ini'].initial = (date.today() + relativedelta(months=1)).strftime('%Y-%m-%d')
        if self.instance and self.instance.pk:
            estado = self.instance.estado
            if estado != 'X':
                campos_solo_lectura = ['cod_cre', 'cap_ini', 'num_cuo_ini', 'num_cuo_gra', 'tian_ic_ini', 'cod_lin_cre',
                                       'fec_des', 'decreciente', 'tian_pol_seg', 'per_ano', 'fec_pag_ini', 'val_cuo_ini',
                                       'tian_im', 'imputacion', 'libranza', 'pagare', 'termino', 'rep_cen_rie',
                                       'figarantias', 'num_cuo_act', 'val_cuo_act', 'val_gar_hip']
                for field in campos_solo_lectura:
                    self.fields[field].widget.attrs['readonly'] = True
    cod_cre = forms.CharField(required=False, widget=forms.TextInput(attrs={'id': 'form_cod_cre'}))
    doc_ide = forms.CharField(required=False, widget=forms.TextInput(attrs={'id': 'form_doc_ide'}))
    nom_soc = forms.CharField(required=False, widget=forms.TextInput(attrs={'id': 'form_nom_soc'}))
    
    # forms.py
from django import forms
from .models import CREDITOS
from justo_app.opciones import  OPC_EST_CRE

class CreditosFilterForm(forms.Form):
    estado = forms.ChoiceField(
        choices=[('', 'Todos')] + list(OPC_EST_CRE),
        required=False,
        label="Estado",
        initial='A'  # Valor por defecto establecido a 'activo'
    )
    cod_cre = forms.CharField(required=False, max_length=10, label="Código Crédito")
    nombre_deudor = forms.CharField(required=False, label="Nombre del Deudor")
    cod_aso = forms.CharField(required=False, label='Código Asociado')


from django import forms
from .models import CODEUDORES

class CodeudorForm(forms.ModelForm):
    class Meta:
        model = CODEUDORES
        fields = ['tercero']  # Ajusta según los campos que quieras editar