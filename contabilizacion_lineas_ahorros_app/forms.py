from django.shortcuts import render
from django import forms
from .models import LINEAS_AHORRO

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = LINEAS_AHORRO
        fields = "__all__"
        
