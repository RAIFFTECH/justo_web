from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import Lista, Detalle, Crear, Actualizar, ImprimePDF, Eliminar, ExportExcel, ExportPDF

# from .views import Crear, Lista, Detalles, Actualizar, Eliminar, ImprimirPDF, ImprimePDF, ExportarView
from django.conf.urls.static import static

urlpatterns = [
    # Para mostrar formulario de alta de nuevo registro
    # path('crear/', Crear.as_view(), name='crear'),

    # Para mostrar todos los registros en una tabla
    path('lista/', Lista.as_view(), name='listar_estado_financiero'),
    path("detalle/<int:pk>/", Detalle.as_view(), name="detalle_financiero"),
    path("crear/", Crear.as_view(), name="crear_financiero"),
    path('actualizar/<int:pk>/', Actualizar.as_view(), name='actualizar_financiero'),
    path('imprimePDF/<int:pk>/', ImprimePDF.as_view(), name='imprime_pdf'),
    path('eliminar/<int:pk>/', Eliminar.as_view(), name='eliminar_financiero'),
    path('exportar/', ExportExcel.as_view(), name='exportar_excel_financiero'),

    path('exportar-pdf/<int:pk>', ExportPDF.as_view(), name='exportar_pdf_estados'),

    # Para mostrar una página con el detalle del registro



]
