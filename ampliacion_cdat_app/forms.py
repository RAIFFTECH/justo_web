from django.shortcuts import render
from django import forms
from .models import CTA_CDAT_AMP

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CTA_CDAT_AMP
        fields = "__all__"
        
