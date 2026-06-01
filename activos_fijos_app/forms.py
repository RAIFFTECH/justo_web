from django.shortcuts import render
from django import forms
from .models import ACTIVOS_FIJOS

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = ACTIVOS_FIJOS
        fields = "__all__"
        

from django import forms

class ComprobanteDepreciacionForm(forms.Form):
    mes = forms.ChoiceField(
        choices=[('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
                 ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'),
                 ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')],
        label="Mes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

