from django.shortcuts import render
from django import forms
from .models import CONCEPTOS
# 
class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CONCEPTOS
        fields = "__all__"
        