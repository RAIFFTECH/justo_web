from django.shortcuts import render
from django import forms
from .models import PLAN_CTAS

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = PLAN_CTAS
        # fields = "__all__"
        fields = ['cliente', 'per_con', 'cod_cta', 'nom_cta', 'tip_cta', 'dinamica', 'naturaleza','activa', 'por_tercero', 'cta_act_fij','cta_pre', 'cta_bal', 'cta_res', 'cta_ord', 'cta_ban', 'cta_gan_per', 'cta_per_gan', 'cta_dep', 'cta_ing_ret', 'cta_ret_iva', 'cta_rec']
