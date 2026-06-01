from django.shortcuts import render
from django import forms
from .models import CAMBIOS_CRE

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CAMBIOS_CRE
        fields = "__all__"