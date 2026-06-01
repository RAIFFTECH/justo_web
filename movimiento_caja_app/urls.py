# movimientos_caja_app/urls.py

from django.urls import path
from . import views
from .views import saldos_cajero_dia

urlpatterns = [
    path('list/',views.mov_caja_list , name='mov_caja_list'),
    path('crear/', views.MOV_CAJACreateView.as_view(), name='mov_caja_create'),
    path('editar/<int:pk>', views.MOV_CAJAUpdateView.as_view(), name='mov_caja_update'),
    path('detalle/<int:pk>', views.MOV_CAJADetailView.as_view(), name='mov_caja_detail'),
    path('eliminar/<int:pk>', views.MOV_CAJADeleteView.as_view(), name='mov_caja_delete'),
    #path('imprimir/', views.movimiento_caja, name='movimiento_caja'),
    path('saldos_cajero_dia/', views.saldos_cajero_dia,name='saldos_cajero_dia'),

    path('reporte-caja/', views.reporte_movimientos_caja, name='reporte_caja'),
]
