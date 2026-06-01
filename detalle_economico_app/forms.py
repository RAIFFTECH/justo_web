from django.shortcuts import render
from django import forms
from .models import DETALLE_ECONO

class DetalleEconoForm(forms.ModelForm):
    
    class Meta:
        model = DETALLE_ECONO
        fields = ['detalle_prod', 'cuenta', 'tercero', 'item_concepto','detalle', 'debito', 'credito', 'valor_1', 'valor_2']
