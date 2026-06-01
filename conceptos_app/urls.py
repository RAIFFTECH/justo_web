from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import Crear, Lista, Detalles, Actualizar, Eliminar, ImprimirPDF, ImprimePDF, ExportarView
from django.conf.urls.static import static

urlpatterns = [
    path('crear/', Crear.as_view(), name='crear'),
    path('lista/', Lista.as_view(), name='listar_conceptos'),

    # Para mostrar una página con el detalle del registro
    path('lista/detalles/<int:pk>', Detalles.as_view(), name='detalles'),
    # Para actualizar un registro
    path('lista/actualizar/<int:pk>', Actualizar.as_view(), name='actualizar'),
    # Para eliminar un registro
    path('lista/eliminar/<int:pk>', Eliminar.as_view(), name='eliminar'),
    # Para imprimir un registro
    path('lista/imprime/<int:pk>', ImprimePDF.as_view(), name='imprime'),

    path('lista/imprimir/', ImprimirPDF.as_view(), name='imprimir'),
    path('exportar/', ExportarView.as_view(), name='exportar'),

]
