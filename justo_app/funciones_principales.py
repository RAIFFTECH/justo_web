import re
from datetime import date, datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

def formato_fecha(fecha):
    # Recibe un objeto date y devuelve una cadena tipo Abr-17-2025.
    if not fecha:
        return ""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return ""  # En caso de que la cadena no sea válida
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    return f"{meses[fecha.month - 1]}-{fecha.day:02d}-{fecha.year}"

def formatear_cod_aso(cod_aso):
    # Formatea cod_aso con separador '-' cada tres dígitos de derecha a izquierda.
    return "-".join(re.findall(r".{1,3}", cod_aso[::-1]))[::-1]


def validate_numeric(value):
    if not re.match(r'^[0-9]+$', value):
        raise ValidationError('El número de celular debe contener solo dígitos numéricos.')

class DefaultToZeroMixin(models.Model):
    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if (isinstance(field, models.IntegerField) or isinstance(field, models.FloatField)) and field.attname != 'id' :
                if getattr(self, field.name) is None or getattr(self, field.name) == '':
                    setattr(self, field.name, 0)

        super(DefaultToZeroMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        
        
def fecha_corta(fecha):
    # Recibe un objeto date y devuelve una cadena tipo Abr-17-2025.
    if not fecha:
        return ""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return ""  # En caso de que la cadena no sea válida
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    return f"{meses[fecha.month - 1]}-{fecha.day:02d}-{fecha.year}"


def fecha_larga(fecha):
    # Recibe un objeto date y devuelve una cadena tipo Abril 17 de 2025.
    if not fecha:
        return ""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return ""  # En caso de que la cadena no sea válida
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    return f"{meses[fecha.month - 1]} {fecha.day} de {fecha.year}"

hoy = date.today()


def fecha_año_mes_dia(fecha):
    # Recibe un objeto date y devuelve una cadena tipo 2025-04-17.
    if not fecha:
        return ""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return ""  # En caso de que la cadena no sea válida
    return fecha.strftime("%Y-%m-%d")


def fecha_dia_mes_año(fecha):
    # Recibe un objeto date y devuelve una cadena tipo 17-04-2025.
    if not fecha:
        return ""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return ""  # En caso de que la cadena no sea válida
    return fecha.strftime("%d-%m-%Y")

