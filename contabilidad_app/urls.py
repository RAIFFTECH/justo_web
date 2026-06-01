from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import auxiliar_cuenta, auxiliar_tercero, balance_prueba, balance_general, estado_resultados, auxiliar_comprobante, Buscar_Cuenta_Contable, activos_fijos, conciliacion_bancaria
from django.conf.urls.static import static

urlpatterns = [

    # Para buscar una cuenta contable
    path('buscar/', Buscar_Cuenta_Contable, name='buscar_cuenta_contable'),

    # Para mostrar Balance de Prueba
    path('balance_prueba/', balance_prueba, name='balance_prueba'),

    # Para mostrar Balance General
    path('balance_general/', balance_general, name='balance_general'),
    # path('general/comparativo/', balance_general_comparativo, name='balance_general_comparativo'),

    # Para mostrar Estados de Resultados
    path('estado_resultados/', estado_resultados, name='estado_resultados'),
    # path('resultados/comparativo/', estado_resultados_comparativo, name='estado_resultados_comparativo'),

    # Para actualizar un registro
    # path('auxiliar/tercero/<int:pk>', Actualizar.as_view(), name='auxiliar_tercero'),

    # Para mostrar el Auxiliar por Cuenta
    path('auxiliar/cuenta/', auxiliar_cuenta, name='auxiliar_cuenta'),
    
    # Para mostrar el Auxiliar por Tercero
    path('auxiliar/tercero/', auxiliar_tercero, name='auxiliar_tercero'),

    # Para mostrar el Auxiliar por Comprobante
    path('auxiliar/comprobante/', auxiliar_comprobante, name='auxiliar_comprobante'),

    # Para mostrar Activos Fijos
    path('activos_fijos/', activos_fijos, name='activos_fijos'),

    # Para mostrar Conciliación Bancaria
    path('conciliacion_bancaria/', conciliacion_bancaria, name='conciliacion_bancaria'),

]
