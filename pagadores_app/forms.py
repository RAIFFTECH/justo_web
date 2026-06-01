from django.shortcuts import render
from django import forms
from requests import request
from .models import PAGADORES

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = PAGADORES
        fields = "__all__"
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select rounded-pill', 'readonly': 'readonly'}), 
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.Select(attrs={'class': 'form-select rounded-pill'}),
            'pagador': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_cel': forms.NumberInput(attrs={'class': 'form-control rounded-pill'}),
            }
    
   