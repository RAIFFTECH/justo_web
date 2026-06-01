import django_filters
from .models import HECHO_ECONO

class HechoEconoFilter(django_filters.FilterSet):
    numero = django_filters.CharFilter(field_name='numero', lookup_expr='icontains', label='Número')
    descripcion = django_filters.CharFilter(field_name='descripcion', lookup_expr='icontains', label='Descripción')

    class Meta:
        model = HECHO_ECONO
        fields = ['numero', 'descripcion']
