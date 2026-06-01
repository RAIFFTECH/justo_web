from django.urls import path
from .views import CtasXCobrarListView,CtasXCobrarCreateView,CtasCxcUpdateView,CtasCxcDeleteView,CtasXCobrarImportar
from .views import CtasXCobrarEliminar,descargar_archivo_procesado

urlpatterns = [
    path('listar/',CtasXCobrarListView.as_view(), name='listar_cxc'),
    path('crear/',CtasXCobrarCreateView.as_view(), name='crear_cxc'),
    path('modificar/<int:pk>',CtasCxcUpdateView.as_view(), name='modificar_cxc'),
    path('eliminar/<int:pk>',CtasCxcDeleteView.as_view(), name='eliminar_cxc'),
    path('importar/',CtasXCobrarImportar.as_view(), name='importar_cxc'),
    path('descargar-archivo-procesado/', descargar_archivo_procesado, name='descargar_archivo_procesado'),
    path('eliminar_cxc/',CtasXCobrarEliminar.as_view(), name='eliminar_importar'),
]