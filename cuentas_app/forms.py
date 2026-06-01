from django.shortcuts import render
from django import forms
from .models import PLAN_CTAS

class CrearForm(forms.ModelForm):
    
    class Meta:
        model = PLAN_CTAS
        fields = "__all__"
        widgets = {
            "cliente": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(CrearForm, self).__init__(*args, **kwargs)
        if request and "cliente_id" in request.session:
            self.fields["cliente"].initial = request.session["cliente_id"]
