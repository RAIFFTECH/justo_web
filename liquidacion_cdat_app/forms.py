from django.shortcuts import render
from django import forms
from .models import CTA_CDAT_LIQ

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CTA_CDAT_LIQ
        fields = "__all__"