from django import forms
from .models import CAJEROS
from django.contrib.auth.models import User
from oficinas_app.models import OFICINAS

class CajerosForm(forms.ModelForm):
    # Campos adicionales no pertenecientes directamente al modelo CAJEROS
    doc_ide = forms.CharField(
        required=False, 
        label="Documento Identidad",
        widget=forms.TextInput(attrs={'class': 'form-control'})  # Clase de estilo opcional
    )
    nombre_tercero = forms.CharField(
        required=False, 
        label="Nombre del Tercero",
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})  # Campo solo lectura
    )

    class Meta:
        model = CAJEROS
        fields = ['user', 'oficina', 'fecha_ingreso', 'fecha_retiro', 'activo', 'cta_con_caja', 'cta_con_acre']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'oficina': forms.Select(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_retiro': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cta_con_caja': forms.TextInput(attrs={'class': 'form-control'}),
            'cta_con_acre': forms.TextInput(attrs={'class': 'form-control'}),
        }
        user = forms.ModelChoiceField(queryset=User.objects.all())
        oficina = forms.ModelChoiceField(queryset=OFICINAS.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:  # Verificar si existe una instancia (actualización)
            cajero = kwargs['instance']
            # Verifica si `tercero` no es None antes de acceder a sus atributos
            if cajero is not None:  
                self.fields['doc_ide'].initial = cajero.tercero.doc_ide
                self.fields['nombre_tercero'].initial = cajero.tercero.nombre

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Manejo del campo `doc_ide`
        doc_ide = self.cleaned_data.get('doc_ide')
        if instance.tercero and doc_ide:
            instance.tercero.doc_ide = doc_ide
            instance.tercero.save()  # Guarda el modelo relacionado `tercero`

        if commit:
            instance.save()  # Guarda el modelo `CAJEROS`
        return instance

