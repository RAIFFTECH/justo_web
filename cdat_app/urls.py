from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import CtasCdatsCreateView,CtasCdatListView,buscar_cta_int,CtasCdatsUpdateView,ImprimePDF, ImprimirTitulo
from .views import  generar_reportes_cdat,imprimirRepCdat,guardar_directorio,repCdatsVecidos
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('lista/',CtasCdatListView.as_view(), name='listar_cdats'),
    path('crear/',CtasCdatsCreateView.as_view(), name='crear_cdat'),
    path('actualizar/<int:pk>',CtasCdatsUpdateView.as_view(), name='actualizar_cdat'),
    path('buscar_cta_aho/<str:codigo>',buscar_cta_int, name='buscar_cta_int'),
    path('imprimir/<int:pk>',ImprimePDF.as_view(), name='cdat_amp_imprimir'),
    path('editar/<int:pk>',CtasCdatsCreateView.as_view(), name='imprimir_cdat'),
    path('imprimirRepCdata',ImprimePDF.as_view(), name='imprimirRepCdat'),
    path('reportes/', generar_reportes_cdat, name='generar_reportes_cdat'),
    path('imprimir/', repCdatsVecidos, name='impCdatsVencidos'),
    path("guardar_directorio/", guardar_directorio, name="guardar_directorio"),
    path('imprimir_titulo/<int:pk>', ImprimirTitulo.as_view(), name='imprimir_titulo'),


]
