from django.db import models
from oficinas_app.models import OFICINAS
# Create your models here.

class PLAN_APORTES(models.Model):
    oficina = models.ForeignKey(OFICINAS, on_delete=models.CASCADE, verbose_name='Oficina')
    agno = models.IntegerField(blank=True, null=True, verbose_name='Año')
    meses = models.IntegerField(blank=True, null=True, verbose_name='Meses')
    iniadu = models.FloatField(blank=True, null=True, verbose_name='IniAdu')
    totadu = models.FloatField(blank=True, null=True, verbose_name='TotAdu')
    inichi1 = models.FloatField(blank=True, null=True, verbose_name='IniChi1')
    totchi1 = models.FloatField(blank=True, null=True, verbose_name='TotChi1')
    inichi2 = models.FloatField(blank=True, null=True, verbose_name='IniChi2')
    totchi2 = models.FloatField(blank=True, null=True, verbose_name='TotChi2')
    inijur = models.FloatField(blank=True, null=True, verbose_name='IniJur')
    totjur = models.FloatField(blank=True, null=True, verbose_name='TotJur')

    class Meta:
        unique_together = [['oficina', 'agno']]
        db_table = 'plan_aportes'

    def __str__(self):
        return 