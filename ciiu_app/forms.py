from django.shortcuts import render
from django import forms
from .models import CIIU
from django.core.exceptions import ValidationError

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CIIU
        fields = ['cliente','codigo','actividad']
        widgets = {
                    'codigo': forms.NumberInput(attrs={'class': 'form-control'}),
                    'actividad': forms.TextInput(attrs={'class': 'form-control'}),
        }
