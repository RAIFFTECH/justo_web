from django.db import models
from clientes_app.models import CLIENTES
# Create your models here.
class DESTINO_CRE(models.Model):
    cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    codigo = models.IntegerField(verbose_name='Código')
    descripcion = models.CharField(max_length=50, null=True,verbose_name='Descripción')

    class Meta:
        unique_together = [['cliente', 'codigo']]
        db_table = 'destino_cre'

    def __str__(self):
        return self.descripcion
