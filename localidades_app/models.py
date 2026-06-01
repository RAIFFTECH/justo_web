from django.db import models
# from clientes_app.models import CLIENTES

class LOCALIDADES(models.Model):
    # cliente = models.ForeignKey(CLIENTES, on_delete=models.PROTECT, verbose_name='Cliente')
    codigo = models.CharField(max_length=8, null=False, verbose_name='Código')
    nombre = models.CharField(max_length=36, null=False, verbose_name='Ciudad')
    cod_pos = models.CharField(max_length=12, null=True, verbose_name='Código Postal')
    departamento = models.CharField(max_length=36, null=True, verbose_name='Departamento')

    class Meta:
        unique_together = [['codigo']]
        db_table = 'localidades'

    def __str__(self):
        return self.nombre + '-' +self.departamento
