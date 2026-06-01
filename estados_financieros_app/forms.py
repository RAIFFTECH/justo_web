from django.shortcuts import render
from django import forms
from .models import ESTADOS_FIN

"""
class CrearForm(forms.ModelForm):
    
    class Meta:
        model = PLAN_CTAS
        # fields = "__all__"
        fields = ['cliente', 'per_con', 'cod_cta', 'nom_cta', 'tip_cta', 'dinamica', 'naturaleza','activa', 'por_tercero', 'cta_act_fij','cta_pre', 'cta_bal', 'cta_res', 'cta_ord', 'cta_ban', 'cta_gan_per', 'cta_per_gan', 'cta_dep', 'cta_ing_ret', 'cta_ret_iva', 'cta_rec']
"""


class EstadosForm(forms.ModelForm):
    class Meta:
        model = ESTADOS_FIN
        fields = "__all__"
        widgets = {
            "fec_inf": forms.DateInput(attrs={'type': 'date'}),
            "cliente": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(EstadosForm, self).__init__(*args, **kwargs)
        if request and 'cliente_id' in request.session:
            self.fields['cliente'].initial = request.session['cliente_id']