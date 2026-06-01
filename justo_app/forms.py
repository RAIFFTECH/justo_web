from django.shortcuts import render
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
        

# class CrearForm(forms.ModelForm):
    
#     class Meta:
#         model = REGISTROS
#         fields = ['trabajador','trabajo','cantidad','fecha']
#         widgets = {
#                     'trabajador': forms.TextInput(attrs={'class': 'form-control'}),
#                     'trabajo': forms.TextInput(attrs={'class': 'form-control'}),
#                     'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
#                     'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d'),
#         }

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
