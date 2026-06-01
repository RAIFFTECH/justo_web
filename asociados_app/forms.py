from django.forms import modelformset_factory
from django.shortcuts import render
from django import forms
from .models import ASOCIADOS, ASO_BENEF, ASO_REFERENCIAS


class CrearForm(forms.ModelForm):
    
    class Meta:
        model = ASOCIADOS
        fields = "__all__"
        widgets = {
            # "fec_afi": forms.DateInput(attrs={'type': 'date'}),
            'fec_nac': forms.DateInput(attrs={'type': 'date'}),
            'fec_ac': forms.DateInput(attrs={'type': 'date'}),
            # 'fec_ing_tra': forms.DateInput(attrs={'type': 'date'}),
            'tel_ac': forms.NumberInput(),
            'negocio_tel': forms.NumberInput(),
        }


class BeneficiarioForm(forms.ModelForm):
    class Meta:
        model = ASO_BENEF
        fields = ['cla_doc', 'doc_ide', 'nombre', 'agno_nac', 'parentesco', 'porcentaje']


class ReferenciaForm(forms.ModelForm):
    class Meta:
        model = ASO_REFERENCIAS
        fields = ["tipo_ref", "parentesco", "nombre", "ocupacion", "empresa", "direccion",
                  "tel_fijo", "tel_cel", "tel_emp", "es_fam_dir_cli"]
