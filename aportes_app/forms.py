from django.shortcuts import render
from django import forms
from .models import PLAN_APORTES

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = PLAN_APORTES
        fields = "__all__"
        
