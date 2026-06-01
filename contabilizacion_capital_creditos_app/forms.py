from django.shortcuts import render
from django import forms
from .models import IMP_CON_CRE

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = IMP_CON_CRE
        fields = "__all__"
        
