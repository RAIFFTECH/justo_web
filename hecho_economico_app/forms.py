from django import forms
from .models import HECHO_ECONO
from detalle_producto_app.models import DETALLE_PROD
from django.forms import inlineformset_factory
from localidades_app.models import LOCALIDADES
from cuentas_app.models import PLAN_CTAS
from documentos_app.models import DOCTO_CONTA
from datetime import date
import re
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


def gomonth(fecha, meses):
    return fecha + relativedelta(months=meses)

class HechoEconoForm(forms.ModelForm):
    protegido = forms.BooleanField(required=False, widget=forms.CheckboxInput(), label='Protegido')
    anulado = forms.BooleanField(required=False, widget=forms.CheckboxInput(), label='Anulado')

    cheque = forms.CharField(required=False)  # No obligatorio
    beneficiario = forms.CharField(required=False)  # No obligatorio
    fecha = forms.DateField(
        initial=date.today,  # Fecha actual por defecto
        widget=forms.DateInput(
            attrs={
                'class': 'tu-clase',  
                'type': 'date'
            }
        )
    )

    class Meta:
        model = HECHO_ECONO
        fields = ['docto_conta', 'numero', 'fecha','valor', 'descripcion', 'anulado', 'protegido', 'canal', 'banco', 'cheque', 'beneficiario', 'ciudad']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'limited-width-inputc2', 'style': 'width: 100px;'}),
            'cheque': forms.TextInput(attrs={'class': 'limited-width-inputc2', 'style': 'width: 100px;'}),
            'beneficiario': forms.TextInput(attrs={'class': 'limited-width-inputc3', 'style': 'width: 100px;'}),
            'ciudad': forms.Select(attrs={'class': 'limited-width-inputc4', 'style': 'width: 280px;'}),
            'descripcion': forms.TextInput(attrs={'style': 'width: 440px;'}),
            # 'valor': forms.TextInput(attrs={'disabled': 'disabled'}),
        }

    def __init__(self, *args, **kwargs):
        cliente_id = kwargs.pop('cliente_id', None)
        oficina_id = kwargs.pop('oficina_id', None)
        per_con = kwargs.pop('per_con', None)
        super(HechoEconoForm, self).__init__(*args, **kwargs)
        if self.instance:
            print("Protegido en instancia:", self.instance.protegido)  # Valor del modelo
            self.fields['protegido'].initial = self.instance.protegido == 'S'
            print("Protegido inicial en formulario:", self.fields['protegido'].initial)  # Valor inicial del formulario

            print("Anulado en instancia:", self.instance.anulado)
            self.fields['anulado'].initial = self.instance.anulado == 'S'
            print("Anulado inicial en formulario:", self.fields['anulado'].initial)  # Valor inicial del formulario
        
        self.fields['numero'].widget.attrs.update({
            'style': 'width: 100%; max-width: 200px;',  # Ajusta según sea necesario
            'maxlength': '10', 'class': 'readonly-field',
        })
        #'maxlength': '10', 'readonly' : 'readonly', 'class': 'readonly-field',
        self.fields['fecha'].widget.attrs.update({
            'style': 'width: 120%; max-width: 300px;',  # Ajusta según sea necesario
        })
        self.fields['beneficiario'].widget.attrs.update({
            'style': 'width: 120%; max-width: 360px;',  # Ajusta según sea necesario
        })

        if cliente_id and oficina_id and per_con:
            docto_conta_queryset = DOCTO_CONTA.objects.filter(oficina__cliente_id=cliente_id, oficina_id=oficina_id, per_con=per_con)
            docto_conta_choices = [(None, 'Seleccionar')]  
            for dc in docto_conta_queryset:
                docto_conta_choices.append((dc.id, f'{dc.codigo} - {dc.nombre}'))
            self.fields['docto_conta'].choices = docto_conta_choices
            for option in self.fields['docto_conta'].widget.choices:
                if option[0] is not None:
                    dc = next((dc for dc in docto_conta_queryset if dc.id == option[0]), None)
                    if dc:
                        option = option + (dc.num_automatico,)
                else:
                    option = option + (None,)
            self.fields['docto_conta'].widget.attrs.update({'onchange': 'updateNumAutomatico()'})

            banco_queryset = PLAN_CTAS.objects.filter(per_con=per_con, tip_cta='A', cta_ban='S')
            banco_choices = [(None, 'Seleccionar')]  # Opción predeterminada
            banco_choices += [(bc.id, f'{bc.cod_cta} - {bc.nom_cta}') for bc in banco_queryset]
            self.fields['banco'].choices = banco_choices

            ciudad_queryset = LOCALIDADES.objects.filter(cliente_id=cliente_id)
            ciudad_choices = [(lo.id, f'{lo.nombre} - {lo.departamento[:5]} - {lo.codigo}') for lo in ciudad_queryset]
            self.fields['ciudad'].choices = ciudad_choices
            self.fields['banco'].required = False

   
    def clean(self):
        cleaned_data = super().clean()
        print('Datos del formulario (POST):', cleaned_data)
        docto_conta = cleaned_data.get("docto_conta")
        numero = cleaned_data.get("numero")
        print('Instance PK en clean:------------->  ', self.instance.pk)  
        if self.instance.pk:
            if HECHO_ECONO.objects.filter(docto_conta=docto_conta, numero=numero).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ya existe otro registro con este documento y número.")
        else:
            if HECHO_ECONO.objects.filter(docto_conta=docto_conta, numero=numero).exists():
                raise forms.ValidationError("Ya existe un registro con este documento y número.")
        return cleaned_data
   
    def clean_protegido(self):
        value = self.cleaned_data.get('protegido', False)
        return 'S' if value else 'N'

    def clean_anulado(self):
        value = self.cleaned_data.get('anulado', False)
        return 'S' if value else 'N'
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha > date.today():
            raise forms.ValidationError('La fecha no puede ser posterior a la fecha actual')
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

# Crear un formset para manejar varios detalles del producto
DetalleProdFormset = inlineformset_factory(
    HECHO_ECONO,
    DETALLE_PROD,
    form=DetalleProdForm,
    extra=1,
    can_delete=True
)



