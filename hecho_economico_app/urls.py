from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views_ini import get_documentos,get_comprobantes,index,get_canales,get_ciudades,get_bancos,buscar_beneficiarios,hecho_detalles_lista,buscar_conceptos
from .views_ini import buscar_subcuenta,validar_concepto_subcuenta
from django.conf.urls.static import static
from django.urls import path
from .views import HechoEconoCreateView, HechoEconoUpdateView,confirmar_eliminar_hecho_econo
from .views import buscar_hechos_econo, get_consecutivo_plus_one,ImprimePdf
from django.urls import path

urlpatterns = [
    path('documentos/<int:agno>',get_documentos,name = 'documentos'),
    path('compro/<int:docto_id>',get_comprobantes,name='get_compro'),
    path('canales/',get_canales,name='get_canales'),
    path('ciudades/',get_ciudades,name='get_ciudades'),
    path('beneficiarios/',buscar_beneficiarios,name='get_beneficiarios'),
    path('conceptos/',buscar_conceptos,name='get_conceptos'),
    path('subcuenta/',buscar_subcuenta,name='get_subcuentas'),
    path('concepto_subcuenta/',validar_concepto_subcuenta,name='validar_concepto_subcuenta'),
    path('hecho_prod/<int:hecho_id>',hecho_detalles_lista,name='hecho_prod'),
    path('hecho_econo/create/', HechoEconoCreateView.as_view(), name='hecho_econo_create'),
    path('hecho_econo/editar/<int:pk>', HechoEconoUpdateView.as_view(), name='hecho_econo_update'),
    path('hecho_econo/eliminar/<int:pk>',confirmar_eliminar_hecho_econo, name='hecho_econo_delete'),
    path('hecho_econo/imprime/<int:pk>',ImprimePdf.as_view(), name='imprime_comprobante'),
    path('buscar/',buscar_hechos_econo, name='buscar_hechos_econo'),   #  ok
    path('get_consecutivo_plus_one/',get_consecutivo_plus_one, name='get_consecutivo_plus_one'),
    # path('hecho_econo/imprime/<int:pk>', ImprimePdf.as_view(), name='imprime_comprobante'),
]    
