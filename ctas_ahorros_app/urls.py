from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import ImprimirPDF,ImprimePDF,ExportarView,CtasAhorroCreateView,CtasAhorroUpdateView,CtasAhorroDeleteView
from .views import CtasAhorroListView,BuscarCtaAhoView
from .views import liquidar_ctas_ahorro,listar_movtos_cta_ahorro,obtener_titular_cta_aho
from django.conf.urls.static import static
from .views import max_consecutivo_view

urlpatterns = [
    path('max-consecutivo/', max_consecutivo_view, name='max_consecutive_view'),
    path('lista/',CtasAhorroListView.as_view(), name='listar_ctas_ahorros'),
    path('cuentas/create/', CtasAhorroCreateView.as_view(), name='ctas_ahorro_create'),
    path('cuentas/update/<int:pk>/', CtasAhorroUpdateView.as_view(), name='ctas_ahorro_update'),
    path('buscar/',BuscarCtaAhoView.as_view(), name='buscar_cta_aho'),
    path('lista/imprime/<int:pk>', ImprimePDF.as_view(), name='cdat_amp_imprime'),
    path('lista/imprimir/', ImprimirPDF.as_view(), name='total_ctas_aho_imp'),
    path('exportar/', ExportarView.as_view(), name='exportar'),
    path('saldos_fecha/',liquidar_ctas_ahorro, name='saldos_ahorros_fecha'),   
    path('movtos_cta_aho/',listar_movtos_cta_ahorro, name='movtos_cta_ahorro'), 
    path('titular_cta_aho/<str:num_cta>/',obtener_titular_cta_aho, name='obtener_nom_titular'),
]
