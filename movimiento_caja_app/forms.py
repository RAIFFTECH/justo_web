from django.shortcuts import render
from .models import MOV_CAJA
from cajeros_app.models import CAJEROS
from datetime import date
from django import forms
from .models import MOV_CAJA, CAJEROS

class MovCajaForm(forms.ModelForm):
    monedas = forms.CharField(
        widget=forms.Textarea,
        help_text="Ingrese las denominaciones en formato JSON. Ejemplo: [{\"denominacion\": 100, \"numero\": 5}, {\"denominacion\": 50, \"numero\": 10}]"
    )

    class Meta:
        model = MOV_CAJA
        fields = [
            'cajero', 'fecha', 'jornada', 'saldo_ini', 
            'debitos', 'creditos', 'val_che_dev', 
            'saldo_fin', 'diferencia', 'val_cheques', 
            'val_vales', 'cerrado', 'monedas'
        ]
        widgets = {
            'cajero': forms.Select(attrs={'class': 'form-control border border-secondary rounded'}), 
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control border border-secondary rounded'}),
            'jornada': forms.TextInput(attrs={'class': 'form-control border border-secondary rounded'}),
            'saldo_ini': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'debitos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'creditos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'val_che_dev': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'saldo_fin': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'diferencia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'val_cheques': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'val_vales': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cerrado': forms.Select(attrs={'class': 'form-control border border-secondary rounded'}), 
            'monedas': forms.Textarea(attrs={'class': 'form-control'}),

        }

    # Campo 'cajero' para selección
    cajero = forms.ModelChoiceField(queryset=CAJEROS.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        # Establecer la fecha de hoy solo si la instancia no existe (creación)
        if not self.instance.pk:  # Verifica si la instancia tiene un ID, es decir, si es nueva
            self.fields['fecha'].initial = date.today()  # Establece la fecha actual
        else:
            # Si la instancia ya existe (actualización), la fecha se mantiene igual a la que ya tiene la instancia
            self.fields['fecha'].initial = self.instance.fecha  # Mantiene la fecha actual en el caso de actualización

        # Si estamos actualizando, asignamos los valores del `tercero`
        if 'instance' in kwargs:  # Verifica si existe una instancia (actualización)
            cajero = kwargs['instance']
            if cajero is not None and cajero.tercero:  # Verifica si el cajero tiene un `tercero`
                self.fields['doc_ide'].initial = cajero.tercero.doc_ide
                self.fields['nombre_tercero'].initial = cajero.tercero.nombre


class MovCajaFilterForm(forms.Form):
    fecha_inicio = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_fin = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    cajero = forms.ModelChoiceField(
        queryset=MOV_CAJA.objects.values_list('cajero', flat=True).distinct(),
        required=False,
        empty_label="Seleccione un cajero"
    )
