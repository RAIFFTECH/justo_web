from django.shortcuts import render
from django import forms
from .models import CENTROCOSTOS

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CENTROCOSTOS
        fields = "__all__"
        # widgets = {'oficina': forms.TextInput(attrs={'class': 'form-control rounded-pill'}),
        #            'codigo': forms.TextInput(attrs={'class': 'form-control rounded-pill'}),
        #            'centro_costo': forms.TextInput(attrs={'class': 'form-control rounded-pill'})
        #            }
        
