from django.shortcuts import render
from django import forms
from .models import ORIGINACION


class CrearForm(forms.ModelForm):
    
    class Meta:
        model = ORIGINACION
        fields = "__all__"