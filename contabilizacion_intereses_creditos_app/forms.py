from django.shortcuts import render
from django import forms
from .models import IMP_CON_CRE_INT

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = IMP_CON_CRE_INT
        fields = "__all__"
        
