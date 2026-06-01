from django import forms
from terceros_app.models import TERCEROS
from detalle_producto_app.models import DETALLE_PROD
from .models import HECHO_ECONO
from documentos_app.models import DOCTO_CONTA
from cuentas_app.models import PLAN_CTAS
from localidades_app.models import LOCALIDADES

import re
from django.forms import inlineformset_factory
from datetime import date 

class HechoEconoForm(forms.ModelForm):
    protegido = forms.BooleanField(required=False, initial=False, label='Protegido')
    anulado = forms.BooleanField(required=False, initial=False, label='Anulado')
    fecha = forms.DateField(
        initial=date.today,  # Establece la fecha actual como valor predeterminado
        widget=forms.DateInput(
            attrs={
                'class': 'tu-clase',  # Aplica las clases CSS necesarias
                'type': 'date'
            }
        )
    )

    class Meta:
        model = HECHO_ECONO
        fields = ['docto_conta', 'numero', 'fecha', 'descripcion', 'anulado', 'protegido', 'canal','banco','cheque','beneficiario','ciudad']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'limited-width-inputc2', 'style': 'width: 100px;'}),
            'cheque': forms.TextInput(attrs={'class': 'limited-width-inputc2', 'style': 'width: 100px;'}),
            'beneficiario': forms.TextInput(attrs={'class': 'limited-width-inputc3', 'style': 'width: 100px;'}),
            'ciudad': forms.Select(attrs={'class': 'limited-width-inputc4', 'style': 'width: 280px;'}),
            'descripcion': forms.TextInput(attrs={'style': 'width: 440px;'}),
        }


    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        oficina_id = kwargs.pop('oficina_id', None)
        per_con = kwargs.pop('per_con', None)
        super(HechoEconoForm, self).__init__(*args, **kwargs)
        self.fields['numero'].widget.attrs['readonly'] = False

        if cliente_id and oficina_id and per_con:
            docto_conta_queryset = DOCTO_CONTA.objects.filter(oficina__cliente_id=cliente_id, oficina_id=oficina_id, per_con=per_con)
            docto_conta_choices = [(dc.id, f'{dc.codigo} - {dc.nombre}') for dc in docto_conta_queryset]
            self.fields['docto_conta'].choices = docto_conta_choices
            banco_queryset = PLAN_CTAS.objects.filter(per_con = per_con, tip_cta='A', cta_ban='S')
            banco_choices = [(pc.id, f'{pc.cod_cta} - {pc.nom_cta[:31]}') for pc in banco_queryset]
            banco_choices.insert(0, (None, 'Seleccionar'))
            self.fields['banco'].choices = banco_choices 
            ciudad_queryset = LOCALIDADES.objects.filter(cliente_id=cliente_id)
            ciudad_choices = [(lo.id, f'{lo.nombre} - {lo.departamento[:5]} - {lo.codigo}') for lo in ciudad_queryset]
            self.fields['ciudad'].choices = ciudad_choices 

    def clean_protegido(self):
        protegido = self.cleaned_data.get('protegido')
        return 'S' if protegido else 'N'

    def clean_anulado(self):
        anulado = self.cleaned_data.get('anulado')
        return 'S' if anulado else 'N'

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', fecha):
            raise forms.ValidationError('La fecha debe estar en formato dd/mm/yyyy')
        # Aquí puedes agregar más validaciones para la fecha si es necesario
        return fecha

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if len(descripcion) < 5:
            raise forms.ValidationError('La descripción debe tener al menos 5 caracteres')
        return descripcion


class DetalleProdForm(forms.ModelForm):
    class Meta:
        model = DETALLE_PROD
        fields = ['id', 'concepto', 'subcuenta', 'valor']
        

DetalleProdFormset = inlineformset_factory(
    HECHO_ECONO,
    DETALLE_PROD,
    form = DetalleProdForm,
    extra = 1,
    can_delete = True
)
