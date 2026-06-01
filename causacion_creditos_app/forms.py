from django.shortcuts import render
from django import forms
from .models import CREDITOS_CAUSA

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CREDITOS_CAUSA
        fields = "__all__"
        
