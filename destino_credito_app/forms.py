from django.shortcuts import render
from django import forms
from .models import DESTINO_CRE

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = DESTINO_CRE
        fields = '__all__'