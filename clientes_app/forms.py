from django.shortcuts import render
from django import forms
from .models import CLIENTES

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = CLIENTES
        fields = ['codigo','doc_ide','dv','sigla','nombre','direccion','telefono','celular','ciudad','email','dominio','nit_ger','nom_ger','nit_con','nom_con','tp_con','nit_rev_fis','nom_rev_fis','tp_rev_fis','age_ret','ret_iva','aut_ret','logo','num_lic','lic_act','ini_lic','fin_lic']
