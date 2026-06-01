from django.db import models
from django.db import models
from oficinas_app.models import OFICINAS
from terceros_app.models import TERCEROS
from justo_app.opciones import OPC_BOOL
from django.contrib.auth.models import User
from PIL import Image

class CAJEROS(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name='Usuario')
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT, null=True, verbose_name='Oficina')
    tercero = models.ForeignKey(TERCEROS, on_delete=models.SET_NULL, null=True, verbose_name='Tercero')
    fecha_ingreso = models.DateField(null=True, blank=False,verbose_name = 'Fecha Ingreso Cajero')
    fecha_retiro = models.DateField(null=True, blank=True,verbose_name = 'Fecha Retiro Cajero')
    activo = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Está Activo?')
    cta_con_caja = models.CharField(max_length=10,null=False, blank=False,verbose_name = 'Cta Contable caja')
    cta_con_acre = models.CharField(max_length=10,null=False, blank=False,verbose_name = 'Cta Contable Acreedores')
    
    class Meta:
        unique_together = [['user','oficina']]
        db_table = 'cajeros' 
        
    def __str__(self):
        # Devuelve el nombre del usuario asociado al cajero o alguna otra combinación relevante.
        return f"{self.user.username} - {self.tercero.nombre }"