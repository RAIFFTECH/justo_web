from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import cifin, datacredito, CatRecPerEsp, cartera_fecha,cartera_super,liquidar_asiento,ejecutar_modelo
from .views import iniciar_modelo,progreso_modelo,ejecutar_tarea,ejecutar_rec_pe,ver_resumen_pe
from .views import indicador_de_cartera,riesgo_de_liquidez_cartera,exportar_catego_pe,exportar_rpki_pe,exportar_asiento_pe
from .views import deterioro_de_cartera
from django.conf.urls.static import static

urlpatterns = [
    path('cifin/', cifin, name='cifin'),
    path('datacredito/', datacredito, name='datacredito'),
    path('cartera_fecha/', cartera_fecha, name='cartera_fecha'),
    path('indicador_cartera/',indicador_de_cartera, name='indicador_de_cartera'),
    path('cartera_super/', cartera_super, name='cartera_super'),
    path('reclasificacion/',CatRecPerEsp.as_view(), name='reclasificacion'),
    path('liquidar_asiento/<int:numero>/',liquidar_asiento, name='liquidar_asiento'),
    path('ejecutar-modelo/',ejecutar_modelo, name='ejecutar_modelo'),
    path('ejecutar-rec_pe/',ejecutar_rec_pe, name='ejecutar_rec_pe'),
    path('ver-resumen_pe/<str:fecha>/',ver_resumen_pe, name='ver_resumen_pe'),
    path('iniciar-modelo/', iniciar_modelo, name='iniciar_modelo'),
    path('progreso-modelo/<str:task_id>/',progreso_modelo, name='progreso_modelo'),
    path('ejecutar/',ejecutar_tarea, name='ejecutar_tarea'),
    path('RieLiqCartera/',riesgo_de_liquidez_cartera, name='rie_liq_cartera'),
    path('comprobante_pe/<str:fecha>/',exportar_asiento_pe,name='comprobante_pe'),
    path('catego_pe/<str:fecha>/',exportar_catego_pe,name='catego_pe'),
    path('rpki_pe/<str:fecha>/',exportar_rpki_pe,name='rpki_pe'),
    path('deterioro_de_cartera/<str:fecha>/',deterioro_de_cartera,name='deterioro_de_cartera'),
]
