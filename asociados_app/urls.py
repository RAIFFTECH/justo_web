from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import Crear, Lista, Detalles, Actualizar, Eliminar, ImprimirPDF, ImprimePDF
from .views import obtener_socio, ExportPDF, CrearBeneficiarios, CrearReferencia, listado_mensual_asociados
from .views import asociados_super, estado_cuenta, enviar_email,calificacion_socio
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('crear/', Crear.as_view(), name='crear'),
    path('lista/', Lista.as_view(), name='listar_asociados'),
    path('lista/detalles/<int:pk>', Detalles.as_view(), name='detalles'),
    path('lista/actualizar/<int:pk>', Actualizar.as_view(), name='actualizar'),
    path('lista/eliminar/<int:pk>', Eliminar.as_view(), name='eliminar'),
    path('lista/imprime/<int:pk>', ImprimePDF.as_view(), name='imprime'),
    path('lista/imprimir/', ImprimirPDF.as_view(), name='imprimir'),
    #path('exportar/', ExportarView.as_view(), name='exportar'),
    path('obtener/<str:cod_aso>',obtener_socio, name='obtener_socio'),
    path('exportar-pdf/<int:pk>', ExportPDF.as_view(), name='exportar_pdf_asociado'),
    path('crear-beneficiario/<int:pk>', CrearBeneficiarios.as_view(), name='crear_beneficiario'),
    path('crear-referencia/<int:pk>', CrearReferencia.as_view(), name='crear_referencia'),
    path('mensuales/', listado_mensual_asociados, name='listado_mensual_asociados'),
    path('asociados_supersolidaria/', asociados_super, name='asociados_super'),
    path('estado_cuenta/<int:pk>', estado_cuenta, name='estado_cuenta_asociado'),
    path('calificacion_socio/<int:pk>', calificacion_socio, name='calificacion_socio'),
    path('enviar_estado_cuenta/<int:pk>', enviar_email, name='enviar_email'),
]
