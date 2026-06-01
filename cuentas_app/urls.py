from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import Crear, Lista, Detalles, Actualizar, Eliminar, ImprimirPDF, ImprimePDF, ExportarView, ExportPDF, Buscar_Cuenta_Contable
from django.conf.urls.static import static

urlpatterns = [
    # Para mostrar formulario de alta de nuevo registro
    path('crear/', Crear.as_view(), name='crear'),

    # Para mostrar todos los registros en una tabla
    path('lista/', Lista.as_view(), name='listar_cuenta'),

    # Para mostrar una página con el detalle del registro
    path('lista/detalles/<int:pk>', Detalles.as_view(), name='detalles'),

    # Para buscar una cuenta contable
    path('buscar/<str:template_name>/', Buscar_Cuenta_Contable, name='buscar_cuenta_contable'),
    path('lista/detalles/<int:pk>', Detalles.as_view(), name='detalles'),

    # Para actualizar un registro
    path('lista/actualizar/<int:pk>', Actualizar.as_view(), name='actualizar'),

    # Para eliminar un registro
    path('lista/eliminar/<int:pk>', Eliminar.as_view(), name='eliminar'),

    # Para imprimir un registro
    path('lista/imprime/<int:pk>', ImprimePDF.as_view(), name='imprime'),

    # Para imprimir todos los registros
    path('lista/imprimir/', ImprimirPDF.as_view(), name='imprimir'),

    # Para exportar los registros
    path('exportar/', ExportarView.as_view(), name='exportar'),

    path('exportar-pdf/<int:pk>', ExportPDF.as_view(), name='exportar_pdf_cuenta'),

]
