from django.shortcuts import render
from django import forms
from .models import CAT_DES_DIA_CRE

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CAT_DES_DIA_CRE
        fields = "__all__"
        
