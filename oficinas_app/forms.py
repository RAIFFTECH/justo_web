from django.shortcuts import render
from django import forms
from .models import OFICINAS

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = OFICINAS
        fields = ['cliente','codigo','nombre_oficina','responsable','celular','email','contabiliza']


