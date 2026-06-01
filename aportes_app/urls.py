from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import Crear, Lista, Detalles, Actualizar, Eliminar, movtos_aporte_socio, liquidar_aportes, saldo_aportes_fecha, saldo_aportes, aportes_super
# from django.conf.urls.static import static


urlpatterns = [
    path('crear/', Crear.as_view(), name='crear'),
    path('lista/', Lista.as_view(), name='listar_aporte'),
    path('lista/detalles/<int:pk>', Detalles.as_view(), name='detalles'),
    path('lista/actualizar/<int:pk>', Actualizar.as_view(), name='actualizar'),
    path('lista/eliminar/<int:pk>', Eliminar.as_view(), name='eliminar'),
    # path('lista/imprime/<int:pk>', ImprimePDF.as_view(), name='imprime'),
    # path('lista/imprimir/', ImprimirPDF.as_view(), name='imprimir'),
    # path('exportar/', ExportarView.as_view(), name='exportar'),
    path('aporte_socio/', movtos_aporte_socio, name='movtos_apo_soc'),
    path('list_aportes/', liquidar_aportes, name='list_aportes'),
    path('saldo_aportes/', saldo_aportes, name='saldo_aportes'),
    path('aportes_supersolidaria/', aportes_super, name='aportes_super'),
]
