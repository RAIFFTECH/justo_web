from django.shortcuts import render
from django import forms
from .models import LINEAS_AHORRO

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = LINEAS_AHORRO
        fields = "__all__"
        widgets = {'cliente': forms.Select(attrs={'class': 'form-select rounded-pill'}),
                   'cod_lin_aho': forms.Select(attrs={'class': 'form-select rounded-pill'}),
                   'nombre': forms.TextInput(attrs={'class': 'form-control rounded-pill'}),
                   'termino': forms.Select(attrs={'class': 'form-select rounded-pill'}),
                   'per_liq_int': forms.Select(attrs={'class': 'form-select rounded-pill'}),
                   'cta_por_pas': forms.NumberInput(attrs={'class': 'form-control rounded-pill'}),
                   'fec_ult_liq_int': forms.DateInput(attrs={'class': 'form-control rounded-pill'}),
                   'saldo_minimo': forms.NumberInput(attrs={'class': 'form-control rounded-pill'})
                   }
