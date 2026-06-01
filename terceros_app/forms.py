from django.shortcuts import render
from django import forms
from datetime import date
from .models import TERCEROS
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django_select2.forms import Select2Widget


class CrearForm(forms.ModelForm):
    class Meta:
        model = TERCEROS
        fields = "__all__"
        widgets = {
            # "cod_ciu_exp": Select2Widget(attrs={"class": "form-control"}),
            "fec_act": forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d'),
            "fec_exp_ced": forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d'),
            "fec_pep": forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d'),
            "fec_fin_pep": forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d'),
            # "doc_ide": forms.NumberInput(attrs={'type': 'number'}),
            "dig_ver": forms.NumberInput(attrs={'type': 'number'}),
            "nit_rap": forms.NumberInput(attrs={'type': 'number'}),
            "tel_ofi": forms.NumberInput(attrs={'type': 'number'}),
            "tel_res": forms.NumberInput(attrs={'type': 'number'}),
            "celular1": forms.NumberInput(attrs={'type': 'number'}),
            "celular2": forms.NumberInput(attrs={'type': 'number'}),
            "cliente": forms.HiddenInput(),
            # "grupos_especiales": forms.SelectMultiple(attrs={'class': 'form-control'})
            "grupos_especiales": forms.SelectMultiple(attrs={'class': 'form-control', 'disabled': 'disabled'}),
        }

            
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        request = kwargs.pop('request', None)
        super(CrearForm, self).__init__(*args, **kwargs)
        
        # user = kwargs.pop('user', None)
        # super().__init__(*args, **kwargs)
        
        if user:
            self.fields['usuario_asesor'].initial = user.username  # o user si es FK
            self.fields['usuario_asesor'].disabled = True  # deshabilitar en el formulario

        # Valor inicial para el campo fec_act al crear un nuevo tercero
        if not self.instance.pk:
            self.fields['fec_act'].initial = date.today()

        if request and "cliente_id" in request.session:
            self.fields["cliente"].initial = request.session["cliente_id"]

        # Habilitar o deshabilitar el campo según grupo_especial
        grupo_especial_valor = self.instance.grupo_especial if self.instance else None
        if grupo_especial_valor == 'S':
            self.fields['grupos_especiales'].disabled = False
        else:
            self.fields['grupos_especiales'].disabled = True

    
            
    def clean(self):
        cleaned_data = super().clean()
        tip_ter = cleaned_data.get("tip_ter")

        if tip_ter != 'J':
            # Si NO es 'J', pri_ape y pri_nom son obligatorios
            if not cleaned_data.get('pri_ape'):
                self.add_error('pri_ape', 'Este campo es obligatorio para personas naturales.')
            if not cleaned_data.get('pri_nom'):
                self.add_error('pri_nom', 'Este campo es obligatorio para personas naturales.')
        else:
            # Si es 'J', quitar los errores y permitir que estén vacíos
            self.fields['pri_ape'].required = False
            self.fields['pri_nom'].required = False

        return cleaned_data
            