from django.shortcuts import render
from django import forms
from .models import LOCALIDADES
from django.core.exceptions import ValidationError

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = LOCALIDADES
        fields = ['codigo','nombre','cod_pos','departamento']
        widgets = {
                    'codigo': forms.TextInput(attrs={'class': 'form-control solo-numeros'}),
                    'nombre': forms.TextInput(attrs={'class': 'form-control'}),
                    'cod_pos': forms.TextInput(attrs={'class': 'form-control solo-numeros'}),
                    'departamento': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # def clean_codigo(self):
    #     # Obtén el valor del campo 'codigo'
    #     codigo = self.cleaned_data.get('codigo')

    #     # Verifica si el 'codigo' ya existe en la base de datos
    #     if LOCALIDADES.objects.filter(codigo=codigo).exists():
    #         raise ValidationError(
    #             "El código ya existe. Por favor, elija otro.")

    #     # Retorna el valor validado
    #     return codigo

    # def clean_cod_pos(self):
    #     # Obtén el valor del campo 'cod_pos'
    #     cod_pos = self.cleaned_data.get('cod_pos')

    #     # Verifica si el 'cod_pos' ya existe en la base de datos
    #     if LOCALIDADES.objects.filter(cod_pos=cod_pos).exists():
    #         raise ValidationError(
    #             "El código postal ya existe. Por favor, elija otro.")

    #     # Retorna el valor validado
    #     return cod_pos
