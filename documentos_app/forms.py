from django.shortcuts import render
from django import forms
from .models import DOCTO_CONTA

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = DOCTO_CONTA
        fields = ['oficina','per_con','codigo','nom_cto','nombre','doc_admin','doc_caja','inicio_nuevo_per','consecutivo']