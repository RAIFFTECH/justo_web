from django.shortcuts import render
from django import forms
from .models import RET_FUE_AHO

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = RET_FUE_AHO
        fields = '__all__'