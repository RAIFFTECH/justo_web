from django.db import models
from oficinas_app.models import OFICINAS
# Create your models here.
class CENTROCOSTOS(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT,verbose_name='Oficina')
    codigo = models.CharField(max_length=5, null=False,verbose_name='Código')
    centro_costo = models.TextField(verbose_name='Centro de Costo')

    class Meta:
        unique_together = [['oficina', 'codigo']]
        db_table = 'centro_costos'
    
    def __str__(self):
        return self.codigo + ' ' + self.centro_costo
