from django.shortcuts import render
from django import forms
from .models import TAS_LIN_AHO

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = TAS_LIN_AHO
        fields = '__all__'