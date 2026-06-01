from django.shortcuts import render
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from justo_app.opciones import OPC_BOOL


class CrearForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = "__all__"


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user', 'oficina', 'photo', 'bio', 'birth_date', 'activo']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'activo': forms.Select(choices=[('', 'Seleccione'), OPC_BOOL]),
        }
