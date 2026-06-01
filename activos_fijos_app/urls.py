from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import Crear, Lista, Detalles, Actualizar, Eliminar 
from .views import generar_comprobante_view,ver_comprobante_view,exportar_excel,exportar_csv
# from django.conf.urls.static import static


urlpatterns = [
    path('crear/', Crear.as_view(), name='crear'),
    path('lista/', Lista.as_view(), name='listar_activos_fijos'),
    path('lista/detalles/<int:pk>', Detalles.as_view(), name='detalles'),
    path('lista/actualizar/<int:pk>', Actualizar.as_view(), name='actualizar'),
    path('lista/eliminar/<int:pk>', Eliminar.as_view(), name='eliminar'),
    # path('lista/imprime/<int:pk>', ImprimePDF.as_view(), name='imprime'),
    # path('lista/imprimir/', ImprimirPDF.as_view(), name='imprimir'),
    # path('exportar/', ExportarView.as_view(), name='exportar'),
    # path('aporte_socio/', movtos_aporte_socio, name='movtos_apo_soc'),
    # path('list_aportes/', liquidar_aportes, name='list_aportes'),
    # path('saldo_aportes/', saldo_aportes, name='saldo_aportes'),
    # path('activos_supersolidaria/', activos_super, name='activos_super'),
    path('generar-comprobante/', generar_comprobante_view, name='generar_comprobante'),
    path('ver-comprobante/<int:pk>/', ver_comprobante_view, name='ver_comprobante'),
    path('exportar-excel/<int:pk>/', exportar_excel, name='exportar_excel'),
    path('exportar-csv/<int:pk>/', exportar_csv, name='exportar_csv'),
]
