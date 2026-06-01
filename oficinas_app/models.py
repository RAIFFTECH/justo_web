from django.db import models
import re
from django.core.exceptions import ValidationError
from justo_app.funciones_principales import validate_numeric
from justo_app.opciones import OPC_BOOL
from clientes_app.models import CLIENTES
from localidades_app.models import LOCALIDADES


class OFICINAS(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    codigo = models.CharField(max_length=5, null=False, verbose_name='Código Oficina')

    @property
    def CodigoCliente(self):
       return self.Codigo[0]
    contabiliza = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Contabiliza')
    nombre_oficina = models.TextField(verbose_name='Nombre Oficina')
    responsable = models.TextField(verbose_name='Responsable Oficina')
    celular = models.CharField(max_length=10, validators=[validate_numeric],help_text='El número de celular debe contener exactamente 10 dígitos numéricos.',null=True, verbose_name='Celular')
    email = models.EmailField(verbose_name='Email')
    direccion = models.CharField(max_length=80, null=True, verbose_name='Dirección')
    ciudad = models.ForeignKey(LOCALIDADES, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Ciudad')

    class Meta:
        unique_together = [['cliente', 'codigo']]
        db_table = 'oficinas'

    def __str__(self):
        return self.codigo + ' ' + self.nombre_oficina
