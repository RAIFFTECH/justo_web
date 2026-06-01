from django.shortcuts import render
from django import forms
from .models import LINEAS_CREDITO

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = LINEAS_CREDITO
        fields = '__all__'