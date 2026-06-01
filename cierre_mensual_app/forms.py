from django.shortcuts import render
from django import forms
from .models import CIERRE_MES

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CIERRE_MES
        fields = "__all__"
